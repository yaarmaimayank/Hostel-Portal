import sqlite3
from werkzeug.security import generate_password_hash

connection = sqlite3.connect('database.db')

# 1. Create Users Table
connection.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        roll_number TEXT, 
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student'
    )
''')

cursor = connection.cursor()

# 2. Inject Admin Account
cursor.execute("SELECT * FROM users WHERE email='admin@iilm.edu'")
if not cursor.fetchone():
    admin_pw = generate_password_hash('iilm@hostel2026')
    cursor.execute('''
        INSERT INTO users (full_name, email, password, role)
        VALUES ('System Admin', 'admin@iilm.edu', ?, 'admin')
    ''', (admin_pw,))
    print("👑 Admin account created!")

# 3. Inject 5 View-Only Teacher Accounts
teacher_pw = generate_password_hash('Teacher@2026')
teachers = [
    ('Warden / Teacher 1', 'teacher1@iilm.edu'),
    ('Warden / Teacher 2', 'teacher2@iilm.edu'),
    ('Warden / Teacher 3', 'teacher3@iilm.edu'),
    ('Warden / Teacher 4', 'teacher4@iilm.edu'),
    ('Warden / Teacher 5', 'teacher5@iilm.edu')
]

for name, email in teachers:
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (full_name, email, password, role)
            VALUES (?, ?, ?, 'teacher')
        ''', (name, email, teacher_pw))
print("👨‍🏫 5 View-Only Teacher accounts created!")

# 4. Create Complaints Table
connection.execute('DROP TABLE IF EXISTS complaints')
connection.execute('''
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT NOT NULL,
        roll_number TEXT NOT NULL,
        college_email TEXT NOT NULL,
        hostel_name TEXT NOT NULL,
        room_number TEXT NOT NULL,
        issue_title TEXT NOT NULL,
        issue_description TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        date_submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

print("✅ Database initialized successfully!")
connection.commit()
connection.close()
