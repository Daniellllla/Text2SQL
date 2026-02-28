from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
import sqlite3
from tabulate import tabulate
import sqlparse
from sqlite3 import OperationalError

llm = ChatOpenAI(
    api_key="sk-04e09897e8b44fa1bc8fcd4bb8c75d1b",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus", 
)

def run_sql_query(query: str, db_path='deliverycenter.db', return_raw=False):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [d[0] for d in (cursor.description or [])]
        if return_raw:
            return column_names, rows
        if rows:
            res = tabulate(rows, headers=column_names, tablefmt='grid', stralign='center')
            print(res)
            return res
        else:
            return "The query result is empty"
    except sqlite3.Error as e:
        raise e
    finally:
        if conn:
            conn.close()

def extract_schema_prompt(db_path='deliverycenter.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    prompt_lines = []
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()

    for (table_name,) in tables:
        prompt_lines.append(f"{table_name}")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        for col in columns:
            name, col_type, notnull, dflt, pk = col[1], col[2], col[3], col[4], col[5]
            desc = f"{name}: {col_type}"
            prompt_lines.append("  - " + desc)

        prompt_lines.append("")

    conn.close()
    return "\n".join(prompt_lines)

def validate_sql(sql: str, db_path='deliverycenter.db') -> bool:
    try:
        parsed = sqlparse.parse(sql)
        if not parsed:
            return False
    except Exception:
        return False
    forbidden_keywords = ['DROP', 'ALTER', 'DELETE', 'UPDATE', 'INSERT', 'TRUNCATE']
    if any(keyword in sql.upper() for keyword in forbidden_keywords):
        return False
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("EXPLAIN " + sql)
        return True
    except OperationalError:
        return False
    finally:
        conn.close()


def gen_system_prompt(prompt: str, db_path='deliverycenter.db'):
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """
You are a SQL expert. According to the provided table structure and query requirement,
generate executable SQL for sqlite. Reply ONLY with the SQL wrapped in <SQL>...</SQL>.

Example:
A: Calculate the amount of users who use online payment
Q: <SQL>SELECT count(payment_id) FROM payments WHERE payment_method = "ONLINE"</SQL>
"""),
        ("human", """
[Database schema]
{schema}

[Query Requirement]
{input}
"""),
    ])
    schema = extract_schema_prompt(db_path)
    prompt_value = prompt_template.invoke({"input": prompt, "schema": schema})
    res = llm.invoke(prompt_value).content.strip()
    sql = res.replace("<SQL>", "").replace("</SQL>", "").strip()
    if not validate_sql(sql, db_path):
        raise ValueError(f"生成的 SQL 不合法: {sql}")
    return sql


def text2sql(query: str, db_path='deliverycenter.db'):
    sql = gen_system_prompt(query, db_path)
    columns, rows = run_sql_query(sql, db_path, return_raw=True)
    return sql, columns, rows


if __name__ == '__main__':
    print("Welcome to text2sql system")
    sql = gen_system_prompt(
        "Could you help me calculate the average of payment fee using online payment method?"
    )
    print(sql)
    run_sql_query(sql)