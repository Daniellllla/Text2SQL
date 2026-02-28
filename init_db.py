import json
import os
import sqlite3

def load_data(conn, file_path = 'data/schema.sql', db_path = 'deliverycenter.db'):
    with open(file_path, "r", encoding='utf-8') as f:
        data = json.load(f)
    table_name = data['table_name']
    rows = data['sample_rows']
    columns = data['column_names']
    types = data['column_types']

    #create
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
    create_table_sql += ",\n".join([
        f"  {col} {col_type}" for col, col_type in zip(columns, types)
    ])
    create_table_sql += "\n);"

    #insert
    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?']*len(columns))})"

    cursor = conn.cursor()

    cursor.execute(create_table_sql)
    for row in rows:
        values = [row.get(col,None) for col in columns]
        cursor.execute(insert_sql, values)
    print(f"Data is written into table {table_name} successfully")

def exec_sql_file(conn, file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
        conn.executescript(sql_script)

def load_db(file_path = 'data/schema.sql', db_path = 'deliverycenter.db'):
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    exec_sql_file(conn, file_path)

    load_data(conn, "data/channels.json")
    load_data(conn, "data/deliveries.json")
    load_data(conn, "data/drivers.json")
    load_data(conn, "data/hubs.json")
    load_data(conn, "data/orders.json")
    load_data(conn, "data/payments.json")
    load_data(conn, "data/stores.json")

    conn.commit()
    conn.close
    print("Database has initialized completely.")

if __name__ == '__main__':
    load_db()
