#!/usr/bin/env python3
"""
ChatBot Infrastructure DB Setup
Initial setup script to create database schema

Created by: Jeff Peterson 8 Dec 2019
"""
from sqlite3 import OperationalError


def db_setup(conn):
    """Initial configuration of database schema"""
    try:
        with conn:

            questions = """
                CREATE TABLE questions (
                    questionid INTEGER PRIMARY KEY AUTOINCREMENT,
                    qversion INTEGER DEFAULT 1,
                    content TEXT NOT NULL,
                    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
                    createdby TEXT,
                    responsetype TEXT,
                    topics TEXT
                );
            """
            conn.execute(questions)

            question_history = """
                CREATE TABLE question_history (
                    historyid INTEGER PRIMARY KEY,
                    questionid INTEGER,
                    qversion INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    contentdiff TEXT,
                    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
                    createdby TEXT,
                    rationale TEXT,

                    FOREIGN KEY(questionid) REFERENCES questions(questionid)
                );
            """
            conn.execute(question_history)

            users = """
                CREATE TABLE users (
                    userid INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
                    birthsex TEXT CHECK (birthsex IN ('MALE', 'FEMALE', 'DECLINE')),
                    pronouns TEXT
                );
            """
            conn.execute(users)

            responses = """
                CREATE TABLE responses (
                    responseid INTEGER PRIMARY KEY AUTOINCREMENT,
                    userid INTEGER,
                    questionid INTEGER,
                    qversion INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    createdat TEXT DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY(userid) REFERENCES users(userid),
                    FOREIGN KEY(questionid) REFERENCES questions(questionid)
                );

            """
            conn.execute(responses)

    except OperationalError as e:
        if str(e) == 'table questions already exists':
            print("""
                Database file already exists.
                Please remove db file specified in .env at DB_PATH.
                """)
        raise e


if __name__ == '__main__':

    from utils import get_db_conn
    """ this import is here because when the unittests run, they want a module
    scoped import statement e.g. from chatbot_infra.utils import get_db_conn
    and when this file is run from the CLI to envoke this main function, the
    import statement cannot find the module chatbot_infra."""

    conn = get_db_conn()
    db_setup(conn)
    conn.close()
