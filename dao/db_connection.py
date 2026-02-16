from contextlib import contextmanager
import os
import sqlite3


DB_PATH = "app.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


print("DB_PATH =", os.path.abspath(DB_PATH))
