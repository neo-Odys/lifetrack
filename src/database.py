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
def create_habit_table(habit_name):
    sanitized_habit_name = ''.join(c for c in habit_name if c.isalnum() or c == '_')
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS habit_{sanitized_habit_name} (
                date TEXT PRIMARY KEY,
                completed BOOLEAN NOT NULL
            )
        ''')
        conn.commit()

def add_habit_status(habit_name, date, completed):
    sanitized_habit_name = ''.join(c for c in habit_name if c.isalnum() or c == '_')
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            INSERT OR REPLACE INTO habit_{sanitized_habit_name} (date, completed)
            VALUES (?, ?)
        ''', (date, completed))
        conn.commit()

def check_habit_status(habit_name, date):
    sanitized_habit_name = ''.join(c for c in habit_name if c.isalnum() or c == '_')
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT completed FROM habit_{sanitized_habit_name} 
            WHERE date = ?
        ''', (date,))
        
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            return None

def get_all_habit_tables():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'habit_%'")
        return [table[0] for table in cursor.fetchall()]

def get_habit_names():
    tables = get_all_habit_tables()
    return [table[6:] for table in tables]  # Usuwanie prefiksu 'habit_'


create_table()

   
