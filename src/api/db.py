import sqlite3

def make_db():
    db = sqlite3.connect("novaex.db")
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, points INTEGER DEFAULT 0, sites TEXT DEFAULT 'no websites')")