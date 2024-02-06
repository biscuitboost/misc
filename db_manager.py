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
