import sqlite3

connection = sqlite3.connect('database.db')

# Drop the old table so we can create the new one with extra columns
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

print("✅ Database initialized successfully with new fields!")
connection.commit()
connection.close()