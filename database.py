import sqlite3

DB_NAME = 'farm_db.sqlite'

def get_db_connection():
    """Creates a connection to the local SQLite database file with row factory enabled."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
