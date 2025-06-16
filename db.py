import sqlite3
from contextlib import asynccontextmanager

@asynccontextmanager
async def init_db(app):
    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            calories INTEGER NOT NULL
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM foods")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO foods (name, calories) VALUES (?, ?)", [
            ("Apple", 95), ("Banana", 105), ("Orange", 62), ("Mango", 99),
            ("Grapes", 67), ("Pineapple", 82), ("Strawberry", 33),
            ("Avocado", 160), ("Blueberry", 57), ("Kiwi", 42),
            ("Watermelon", 30), ("Pear", 101), ("Peach", 58),
            ("Plum", 46), ("Cherry", 50), ("Fig", 74),
            ("Guava", 68), ("Papaya", 59), ("Pomegranate", 83), ("Coconut", 354)
        ])
        conn.commit()
    conn.close()
    print("✅ SQLite database initialized.")
    yield
