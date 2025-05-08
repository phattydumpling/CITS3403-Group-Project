from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

DB_FILE = 'study_session.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS study_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        details TEXT,
                        unit_code TEXT,
                        productivity_score TEXT,
                        hours TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS assessments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        details TEXT,
                        unit_code TEXT,
                        my_score TEXT,
                        total_score TEXT
                    )''')
        conn.commit()

@app.route('/')
def index():
    return render_template('Study_session.html')


@app.route('/api/<table>/search')
def search(table):
    query = request.args.get('q', '').lower()
    unit_code = request.args.get('unit_code', '').lower()

    allowed_tables = {'study_sessions', 'assessments'}
    if table not in allowed_tables:
        return jsonify([])

    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        sql = f"SELECT * FROM {table} WHERE 1=1"
        params = []

        if unit_code:
            sql += " AND LOWER(unit_code) LIKE ?"
            params.append(f'%{unit_code}%')

        if query:
            sql += " AND (LOWER(details) LIKE ? OR LOWER(unit_code) LIKE ?"
            if table == 'study_sessions':
                sql += " OR LOWER(productivity_score) LIKE ? OR LOWER(hours) LIKE ?)"
                params.extend([f'%{query}%'] * 4)
            else:
                sql += " OR LOWER(my_score) LIKE ? OR LOWER(total_score) LIKE ?)"
                params.extend([f'%{query}%'] * 4)
        else:
            sql += ")"

        c.execute(sql, params)
        rows = c.fetchall()

    return jsonify(rows)

@app.route('/api/<table>/add', methods=['POST'])
def add_entry(table):
    data = request.get_json()
    allowed_tables = {'study_sessions', 'assessments'}
    if table not in allowed_tables:
        return jsonify({'status': 'error', 'message': 'Invalid table'})

    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        if table == 'study_sessions':
            c.execute('INSERT INTO study_sessions (details, unit_code, productivity_score, hours) VALUES (?, ?, ?, ?)',
                      (data['details'], data['unit_code'], data['productivity_score'], data['hours']))
        else:
            c.execute('INSERT INTO assessments (details, unit_code, my_score, total_score) VALUES (?, ?, ?, ?)',
                      (data['details'], data['unit_code'], data['my_score'], data['total_score']))
        conn.commit()
    return jsonify({'status': 'success'})

@app.route('/api/<table>/delete', methods=['POST'])
def delete_entries(table):
    ids = request.get_json().get('ids', [])
    allowed_tables = {'study_sessions', 'assessments'}
    if table not in allowed_tables:
        return jsonify({'status': 'error', 'message': 'Invalid table'})

    if not ids:
        return jsonify({'status': 'error', 'message': 'No IDs to delete'})

    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        placeholders = ','.join('?' for _ in ids)
        sql = f"DELETE FROM {table} WHERE id IN ({placeholders})"
        c.execute(sql, ids)
        conn.commit()

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
