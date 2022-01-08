import sqlite3


class DBHelper:
    def __init__(self, dbname="todo.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        print("creating table")
        stmt = "CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY UNIQUE,username STR NOT NULL,warn INTEGER,ban STR,message_id INTEGER)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_item(self, user_id, user_username, message_id):
        stmt = "INSERT INTO users (id, username, message_id) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET message_id = excluded.message_id"
        args = (user_id, user_username, message_id)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def add_user(self, user_id, user_username, warn):
        stmt = "INSERT INTO users (id, username, warn) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET id = excluded.id"
        args = (user_id, user_username, warn)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def add_warn(self, user_id, user_username, warn):
        stmt = "INSERT INTO users (id, username, warn) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET warn = warn + 1"
        args = (user_id, user_username, warn)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def unwarn(self, user_id, user_username, warn):
        stmt = "INSERT INTO users (id, username, warn) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET warn = warn - 1"
        args = (user_id, user_username, warn)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def count_warn(self, user_id):
        # stmt = "SELECT DISTINCT (warn) FROM users WHERE id=(?)"
        stmt = "SELECT warn FROM users WHERE id IN (?)"
        args = (user_id,)
        self.conn.execute(stmt, args)
        data = self.conn.execute(stmt, args)
        for row in data:
            return row[0]

    def delete_warn(self, user_id, user_username, warn):
        stmt = "INSERT INTO users (id, username, warn) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET id = excluded.id,warn = 0"
        args = (user_id, user_username, warn)
        self.conn.execute(stmt, args)
        self.conn.commit()
