import sqlite3
import os

os.makedirs(os.path.join(os.path.dirname(__file__), '../data'), exist_ok=True)

db_path = os.path.join(os.path.dirname(__file__), '../data/data.db')

def connect_db():
    try:
        return sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"Can't connect to: {e}, again...")
        return None

def create_table():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                hour TEXT NOT NULL,
                activity TEXT NOT NULL
            )
        ''')
        conn.commit()

def add_activity(date, hour, activity):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO activities (id, date, hour, activity)
            VALUES (
                (SELECT id FROM activities WHERE date = ? AND hour = ?),
                ?, ?, ?
            )
        ''', (date, hour, date, hour, activity))
        conn.commit()
        print("Activity saaaaved")

def check_activity(date, hour):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT activity FROM activities 
            WHERE date = ? AND hour = ?
        ''', (date, hour))
        
        result = cursor.fetchone()
        
        if result:
            return result[0] 
        else:
            return None  

create_table()

   
