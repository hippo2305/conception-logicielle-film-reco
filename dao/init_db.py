import sqlite3


DB_PATH = "app.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 🎬 Table film (avec annee)
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
      FOREIGN KEY (id_film) REFERENCES film(id_film),
      FOREIGN KEY (id_actor) REFERENCES actor(id_actor)
    );
    """)

    conn.commit()
    conn.close()
