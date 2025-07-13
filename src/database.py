import sqlite3
import os
from contextlib import contextmanager
from typing import List, Tuple, Optional, Union

# Database configuration
DB_DIR = os.path.join(os.path.dirname(__file__), '../data')
DB_PATH = os.path.join(DB_DIR, 'data.db')

# Ensure data directory exists
os.makedirs(DB_DIR, exist_ok=True)

@contextmanager
def get_db_connection():
    """Context manager for database connections with proper error handling."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        yield conn
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def initialize_database():
    """Initialize all required database tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Activities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                hour TEXT NOT NULL,
                activity TEXT NOT NULL,
                UNIQUE(date, hour)
            )
        ''')
        
        # Todo table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS todo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                task TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if created_at column exists, if not add it
        cursor.execute("PRAGMA table_info(todo)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'created_at' not in columns:
            # Add column with NULL default first
            cursor.execute('''
                ALTER TABLE todo 
                ADD COLUMN created_at TIMESTAMP DEFAULT NULL
            ''')
            
            # Update existing rows with current timestamp
            cursor.execute('''
                UPDATE todo 
                SET created_at = datetime('now') 
                WHERE created_at IS NULL
            ''')
        
        conn.commit()

# Activities functions
def add_activity(date: str, hour: str, activity: str) -> None:
    """Add or update an activity for a specific date and hour."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO activities (date, hour, activity)
            VALUES (?, ?, ?)
        ''', (date, hour, activity))
        conn.commit()

def check_activity(date: str, hour: str) -> Optional[str]:
    """Get activity for a specific date and hour."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT activity FROM activities 
            WHERE date = ? AND hour = ?
        ''', (date, hour))
        
        result = cursor.fetchone()
        return result[0] if result else None

def get_activities_by_date(date: str) -> List[Tuple[str, str]]:
    """Get all activities for a specific date."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT hour, activity FROM activities 
            WHERE date = ? 
            ORDER BY CAST(hour AS INTEGER)
        ''', (date,))
        
        return cursor.fetchall()

# Habits functions
def _sanitize_habit_name(habit_name: str) -> str:
    """Sanitize habit name for safe use in SQL table names."""
    return ''.join(c for c in habit_name if c.isalnum() or c == '_')

def create_habit_table(habit_name: str) -> None:
    """Create a table for tracking a specific habit."""
    sanitized_name = _sanitize_habit_name(habit_name)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS habit_{sanitized_name} (
                date TEXT PRIMARY KEY,
                completed BOOLEAN NOT NULL DEFAULT 0
            )
        ''')
        conn.commit()

def add_habit_status(habit_name: str, date: str, completed: bool) -> None:
    """Add or update habit status for a specific date."""
    sanitized_name = _sanitize_habit_name(habit_name)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            INSERT OR REPLACE INTO habit_{sanitized_name} (date, completed)
            VALUES (?, ?)
        ''', (date, completed))
        conn.commit()

def check_habit_status(habit_name: str, date: str) -> Optional[bool]:
    """Get habit status for a specific date."""
    sanitized_name = _sanitize_habit_name(habit_name)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT completed FROM habit_{sanitized_name} 
            WHERE date = ?
        ''', (date,))
        
        result = cursor.fetchone()
        return bool(result[0]) if result is not None else None

def get_habit_names() -> List[str]:
    """Get all habit names from existing habit tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'habit_%'
        ''')
        
        tables = cursor.fetchall()
        return [table[0][6:] for table in tables]  # Remove 'habit_' prefix

def get_habit_stats(habit_name: str, limit: int = 30) -> List[Tuple[str, bool]]:
    """Get recent habit completion statistics."""
    sanitized_name = _sanitize_habit_name(habit_name)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT date, completed FROM habit_{sanitized_name} 
            ORDER BY date DESC 
            LIMIT ?
        ''', (limit,))
        
        return cursor.fetchall()

# Todo functions
def add_task(date: str, task: str, completed: bool = False) -> int:
    """Add a new task and return its ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if created_at column exists
        cursor.execute("PRAGMA table_info(todo)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'created_at' in columns:
            cursor.execute('''
                INSERT INTO todo (date, task, completed, created_at)
                VALUES (?, ?, ?, datetime('now'))
            ''', (date, task, completed))
        else:
            cursor.execute('''
                INSERT INTO todo (date, task, completed)
                VALUES (?, ?, ?)
            ''', (date, task, completed))
            
        conn.commit()
        return cursor.lastrowid

def get_tasks_by_date(date: str) -> List[Tuple[int, str, str, bool]]:
    """Get all tasks for a specific date."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if created_at column exists
        cursor.execute("PRAGMA table_info(todo)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'created_at' in columns:
            cursor.execute('''
                SELECT id, date, task, completed FROM todo 
                WHERE date = ? 
                ORDER BY created_at ASC
            ''', (date,))
        else:
            cursor.execute('''
                SELECT id, date, task, completed FROM todo 
                WHERE date = ? 
                ORDER BY id ASC
            ''', (date,))
        
        return cursor.fetchall()

def update_task_status(task_id: int, completed: bool) -> None:
    """Update the completion status of a task."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE todo SET completed = ? WHERE id = ?
        ''', (completed, task_id))
        conn.commit()

def update_task_text(task_id: int, new_text: str) -> None:
    """Update the text of a task."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE todo SET task = ? WHERE id = ?
        ''', (new_text, task_id))
        conn.commit()

def delete_task(task_id: int) -> None:
    """Delete a task by its ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM todo WHERE id = ?', (task_id,))
        conn.commit()

def get_task_stats(date: str) -> Tuple[int, int]:
    """Get task completion statistics for a date (completed, total)."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed
            FROM todo 
            WHERE date = ?
        ''', (date,))
        
        result = cursor.fetchone()
        return (result[1] or 0, result[0] or 0)

def get_all_tasks(limit: int = 100) -> List[Tuple[int, str, str, bool]]:
    """Get all tasks with optional limit."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if created_at column exists
        cursor.execute("PRAGMA table_info(todo)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'created_at' in columns:
            cursor.execute('''
                SELECT id, date, task, completed FROM todo 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
        else:
            cursor.execute('''
                SELECT id, date, task, completed FROM todo 
                ORDER BY id DESC 
                LIMIT ?
            ''', (limit,))
        
        return cursor.fetchall()

def cleanup_old_tasks(days_old: int = 30) -> int:
    """Delete tasks older than specified days. Returns number of deleted tasks."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if created_at column exists
        cursor.execute("PRAGMA table_info(todo)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'created_at' in columns:
            cursor.execute('''
                DELETE FROM todo 
                WHERE created_at < datetime('now', '-' || ? || ' days')
            ''', (days_old,))
        else:
            # If no created_at column, we can't delete by date
            print("Warning: created_at column not found. Cannot delete old tasks.")
            return 0
            
        conn.commit()
        return cursor.rowcount

# Database maintenance
def vacuum_database() -> None:
    """Optimize database by running VACUUM command."""
    with get_db_connection() as conn:
        conn.execute('VACUUM')

def get_database_info() -> dict:
    """Get database statistics and information."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get table counts
        tables_info = {}
        
        # Activities count
        cursor.execute('SELECT COUNT(*) FROM activities')
        tables_info['activities'] = cursor.fetchone()[0]
        
        # Todo count
        cursor.execute('SELECT COUNT(*) FROM todo')
        tables_info['todos'] = cursor.fetchone()[0]
        
        # Habit tables count
        habit_names = get_habit_names()
        tables_info['habits'] = {}
        for habit in habit_names:
            sanitized_name = _sanitize_habit_name(habit)
            cursor.execute(f'SELECT COUNT(*) FROM habit_{sanitized_name}')
            tables_info['habits'][habit] = cursor.fetchone()[0]
        
        return tables_info

# Initialize database when module is imported
initialize_database()
