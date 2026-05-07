from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/complaints', methods=['GET', 'POST'])
def manage_complaints():
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.get_json()
        conn.execute(
            '''INSERT INTO complaints 
               (student_name, roll_number, college_email, hostel_name, room_number, issue_title, issue_description) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (data['student_name'], data['roll_number'], data['college_email'], 
             data['hostel_name'], data['room_number'], data['issue_title'], data['issue_description'])
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Complaint submitted successfully!'}), 201

    elif request.method == 'GET':
        complaints = conn.execute('SELECT * FROM complaints ORDER BY date_submitted DESC').fetchall()
        conn.close()
        return jsonify([dict(ix) for ix in complaints])

@app.route('/api/complaints/<int:id>', methods=['PATCH'])
def update_complaint(id):
    data = request.get_json()
    new_status = data['status']
    
    conn = get_db_connection()
    conn.execute('UPDATE complaints SET status = ? WHERE id = ?', (new_status, id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Status updated successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)