import sqlite3
from config.config import Config, load_config

config: Config = load_config()
conn = sqlite3.connect(config.database.name)


class Database:
    def __init__(self, name):
        self.name = name

    def create_table(self):
        cur = conn.cursor()
        cur.execute(f"""CREATE TABLE IF NOT EXISTS {self.name}
        (user_id INT PRIMARY KEY,
        positions TEXT,
        prices TEXT,
        total INT)
        ;""")
        conn.commit()
        cur.close()
