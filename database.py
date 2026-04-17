import sqlite3

DB_PATH = "bot.db"

def init_db():
    """初始化資料庫，建立所有資料表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            github_username TEXT,
            reminder_interval INTEGER DEFAULT 24,
            timezone TEXT DEFAULT 'Asia/Taipei'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            name TEXT,
            description TEXT,
            goal TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS check_ins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            project_id INTEGER,
            note TEXT,
            checked_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()