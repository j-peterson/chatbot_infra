import os
import sqlite3
from dotenv import load_dotenv, find_dotenv


def get_db_conn(path=None):
    load_dotenv(find_dotenv())
    db_path = os.getenv('DB_PATH') if path is None else path
    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    return conn
