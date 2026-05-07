from flask import Flask, request, jsonify, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) 

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    hashed_pw = generate_password_hash(data['password'])
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO users (full_name, roll_number, email, password, role) VALUES (?, ?, ?, ?, ?)',
            (data['full_name'], data['roll_number'], data['email'], hashed_pw, 'student')
        )
        conn.commit()
        return jsonify({'message': 'Account created successfully!'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already exists!'}), 400
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (data['email'],)).fetchone()
    conn.close()

    if user and check_password_hash(user['password'], data['password']):
        session['user_id'] = user['id']
        session['role'] = user['role']
        session['full_name'] = user['full_name']
        session['email'] = user['email']
        session['roll_number'] = user['roll_number']
        return jsonify({
            'message': 'Login successful', 
            'role': user['role'],
            'full_name': user['full_name']
        }), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/me', methods=['GET'])
def get_current_user():
    if 'user_id' in session:
        return jsonify({
            'role': session['role'],
            'full_name': session['full_name'],
            'email': session['email'],
            'roll_number': session['roll_number']
        })
    return jsonify({'error': 'Not logged in'}), 401

@app.route('/api/complaints', methods=['GET', 'POST'])
def manage_complaints():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.get_json()
        conn.execute(
            '''INSERT INTO complaints 
               (student_name, roll_number, college_email, hostel_name, room_number, issue_title, issue_description) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (session['full_name'], session['roll_number'], session['email'], 
             data['hostel_name'], data['room_number'], data['issue_title'], data['issue_description'])
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Complaint submitted successfully!'}), 201

    elif request.method == 'GET':
        if session['role'] == 'student':
            complaints = conn.execute('SELECT * FROM complaints WHERE college_email = ? ORDER BY date_submitted DESC', (session['email'],)).fetchall()
        else:
            complaints = conn.execute('SELECT * FROM complaints ORDER BY date_submitted DESC').fetchall()
        conn.close()
        return jsonify([dict(ix) for ix in complaints])

# --- UPDATED: TEACHERS CAN PROGRESS/RESOLVE, ADMINS CAN DO ALL ---
@app.route('/api/complaints/<int:id>', methods=['PATCH'])
def update_complaint(id):
    role = session.get('role')
    if role not in ['admin', 'teacher']:
        return jsonify({'error': 'Unauthorized action.'}), 403

    data = request.get_json()
    new_status = data['status']

    # Block teachers from rejecting
    if role == 'teacher' and new_status == 'Rejected':
        return jsonify({'error': 'Only Admins can reject complaints.'}), 403

    conn = get_db_connection()
    conn.execute('UPDATE complaints SET status = ? WHERE id = ?', (new_status, id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Status updated successfully'})

# --- NEW: ADMIN CAN VIEW REGISTERED STUDENTS ---
@app.route('/api/students', methods=['GET'])
def get_students():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db_connection()
    students = conn.execute("SELECT id, full_name, roll_number, email FROM users WHERE role = 'student' ORDER BY id DESC").fetchall()
    total = conn.execute("SELECT COUNT(*) as count FROM users WHERE role = 'student'").fetchone()['count']
    conn.close()
    
    return jsonify({
        'total': total,
        'students': [dict(ix) for ix in students]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
