import sqlite3


def get_db():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db()
    cursor = conn.cursor()

    # 🔥 USERS TABLE (UPDATED)
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user',
        status TEXT DEFAULT 'active',
        expiry TEXT
    )
    """
    )

    # 🔥 LOGS TABLE
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        ip TEXT,
        login_time TEXT
    )
    """
    )

    # 🔥 TASKS TABLE
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        type TEXT,
        data TEXT,
        status TEXT
    )
    """
    )

    conn.commit()
    conn.close()
