import sqlite3

conn = sqlite3.connect("mindless.db", check_same_thread=False)
cursor = conn.cursor()

# Diary table
cursor.execute("""
CREATE TABLE IF NOT EXISTS diary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_date TEXT,
    content TEXT
)
""")

# Todo table
cursor.execute("""
CREATE TABLE IF NOT EXISTS todo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT,
    completed INTEGER
)
""")

# Timetable table
cursor.execute("""
CREATE TABLE IF NOT EXISTS timetable (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time_slot TEXT,
    activity TEXT
)
""")

# Mood table
cursor.execute("""
CREATE TABLE IF NOT EXISTS mood (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mood_date TEXT,
    mood TEXT
)
""")

conn.commit()