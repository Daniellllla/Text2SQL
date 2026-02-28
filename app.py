import os
from flask import Flask, request, jsonify, send_from_directory

from db_chat import text2sql, extract_schema_prompt

app = Flask(__name__, static_folder='static')
try:
    from flask_cors import CORS
    CORS(app)
except ImportError:
    pass

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get('DB_PATH', os.path.join(_BASE_DIR, 'deliverycenter.db'))


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/api/query', methods=['POST'])
def query():
    data = request.get_json() or {}
    question = data.get('question', '').strip()
    if not question:
        return jsonify({'error': 'Please enter a question'}), 400

    try:
        sql, columns, rows = text2sql(question, DB_PATH)
        serializable_rows = []
        for row in rows:
            serializable_rows.append([str(v) if v is not None else None for v in row])
        return jsonify({
            'success': True,
            'sql': sql,
            'columns': columns,
            'rows': serializable_rows,
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        err_msg = str(e) or type(e).__name__
        if '__enter__' in err_msg:
            err_msg = f'{err_msg}(Maybe is the version problem from LangChain/httpx, please run pip install -U langchain-openai httpx)'
        return jsonify({'success': False, 'error': f'failed to execute: {err_msg}'}), 500


@app.route('/api/schema', methods=['GET'])
def schema():
    try:
        schema_text = extract_schema_prompt(DB_PATH)
        return jsonify({'success': True, 'schema': schema_text})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
