from pathlib import Path
import sqlite3


DB_PATH = "app.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    with open(SCHEMA_PATH, encoding="utf-8") as f:
        cur.executescript(f.read())

    conn.commit()
    conn.close()
