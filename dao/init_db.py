import sqlite3


DB_PATH = "app.db"


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS film (
      id_film INTEGER PRIMARY KEY,
      titre TEXT NOT NULL,
      annee INTEGER,
      realisateur TEXT,
      genre TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS actor (
      id_actor INTEGER PRIMARY KEY AUTOINCREMENT,
      nom TEXT NOT NULL UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS casting (
      id_film INTEGER NOT NULL,
      id_actor INTEGER NOT NULL,
      PRIMARY KEY (id_film, id_actor),
      FOREIGN KEY (id_film) REFERENCES film(id_film) ON DELETE CASCADE,
      FOREIGN KEY (id_actor) REFERENCES actor(id_actor) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
      id_user INTEGER PRIMARY KEY AUTOINCREMENT,
      pseudo TEXT NOT NULL UNIQUE,
      email TEXT,
      listfilms TEXT NOT NULL DEFAULT '[]',
      password TEXT NOT NULL,
      role TEXT NOT NULL DEFAULT 'client'
    );
    """)

    # ⭐ Table favorites
    cur.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
      id_user INTEGER NOT NULL,
      id_film INTEGER NOT NULL,
      created_at TEXT DEFAULT (datetime('now')),
      PRIMARY KEY (id_user, id_film),
      FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE CASCADE,
      FOREIGN KEY (id_film) REFERENCES film(id_film) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()
