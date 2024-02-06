import sqlite3
from sqlite3 import Error

DATABASE_PATH = 'path_to_your_database.db'

def create_connection():
    """Create a database connection."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")

def execute_query(query, params=()):
    """Execute a single query against the database."""
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(f"Error executing query: {e}")
    finally:
        if conn:
            conn.close()

def check_diary_name_exists(diary_name):
    """Check if a diary name already exists in the database."""
    query = "SELECT EXISTS(SELECT 1 FROM disposal_diary_info WHERE diary_name = ?)"
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(query, (diary_name,))
        exists = cur.fetchone()[0]
        return exists
    except Error as e:
        print(f"Error checking diary name existence: {e}")
        return None
    finally:
        if conn:
            conn.close()

def view_disposal_diaries():
    """View all disposal diaries."""
    query = "SELECT * FROM disposal_diary_info"
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        for row in rows:
            print(row)
    except Error as e:
        print(f"Error retrieving diaries: {e}")
    finally:
        if conn:
            conn.close()

def delete_disposal_diary(diary_id):
    """Delete a disposal diary and its records."""
    delete_info_query = "DELETE FROM disposal_diary_info WHERE diary_id = ?"
    delete_records_query = "DELETE FROM disposal_diary_records WHERE diary_info_id = ?"
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(delete_records_query, (diary_id,))
        cur.execute(delete_info_query, (diary_id,))
        conn.commit()
        log_action('DELETE', f'Deleted diary and records for diary_id {diary_id}')
    except Error as e:
        print(f"Error deleting diary: {e}")
    finally:
        if conn:
            conn.close()

