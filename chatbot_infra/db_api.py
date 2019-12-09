"""
ChatBot Infrastructure DB API
Business logic to interact with DB

Created by: Jeff Peterson 8 Dec 2019
"""

from collections import namedtuple
from difflib import Differ

from sqlite3 import OperationalError, ProgrammingError, IntegrityError
from functools import wraps


def catch_db_exceptions(func):
    @wraps(func)
    def decorated_func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OperationalError as e:
            # not necessarily under the control of the programmer
            print(f'\nWARNING!: DB OperationalError Encountered: {e}')
            return None
        except (ProgrammingError, IntegrityError) as e:
            # yeah my B
            print(f'\nWARNING!: DB ProgrammingError or IntegrityError Encountered: {e}')
            return None
    return decorated_func_wrapper


def _makediff(old, new):
    """create a string representing the difference between the input args"""
    d = Differ()

    old = old + '\n' if old[-1] != '\n' else old
    new = new + '\n' if new[-1] != '\n' else new

    diff = list(d.compare([old], [new]))
    return ''.join(diff)


@catch_db_exceptions
def create_question(conn, content, createdby=None, topics=None):
    """insert a question to the questions and question history tables"""

    with conn:
        cur = conn.cursor()

        # first, add the question to the questions table
        sql = """
        INSERT INTO questions (
            content,
            createdby,
            responsetype,
            topics
        ) VALUES (?, ?, ?, ?);
        """
        params = (content, createdby, None, topics)
        cur.execute(sql, params)
        questionid = cur.lastrowid
        cur.close()

    # get our newly created question
    new_question = get_question(conn, questionid)

    if new_question is None:
        return

    with conn:
        # second, add the question to the question history table
        sql = """
        INSERT INTO question_history (
            questionid,
            qversion,
            content,
            createdby,
            rationale
        ) VALUES (?, ?, ?, ?, ?);
        """
        params = (
            questionid,
            new_question.qversion,
            content,
            None,
            None)
        conn.execute(sql, params)

    return questionid


@catch_db_exceptions
def update_question(conn, questionid, content, createdby=None, rationale=None):
    """update a question content and add question to question history"""
    questionid = int(questionid)

    # get current question
    old_question = get_question(conn, questionid)

    if old_question is None:
        return

    old_content = old_question.content
    new_qversion = old_question.qversion + 1

    contentdiff = _makediff(old_content, content)

    with conn:
        # update questions table
        sql = """
        UPDATE questions
        SET
            qversion = ?,
            content = ?
        WHERE questionid = ?;
        """
        params = (new_qversion, content, questionid)
        conn.execute(sql, params)

        # insert updated question into question_history
        sql = """
        INSERT INTO question_history (
            questionid,
            qversion,
            content,
            contentdiff,
            createdby,
            rationale
        ) VALUES (?, ?, ?, ?, ?, ?);
        """
        params = (
            questionid,
            new_qversion,
            content,
            contentdiff,
            createdby,
            rationale)
        conn.execute(sql, params)


@catch_db_exceptions
def create_user(conn, name, email=None, phone=None, birthsex=None, pronouns=None):
    """insert a user to the users table"""

    if birthsex and birthsex.upper() not in ['MALE', 'FEMALE', 'DECLINE']:
        birthsex = None   # TODO better error handling

    with conn:
        # add the user to the table
        sql = """
        INSERT INTO users (
            name,
            email,
            phone,
            birthsex,
            pronouns
        ) VALUES (?, ?, ?, ?, ?);
        """
        params = (name, email, phone, birthsex, pronouns)
        cur = conn.cursor()
        cur.execute(sql, params)
        userid = cur.lastrowid
        cur.close()

    return userid


@catch_db_exceptions
def store_response(conn, userid, questionid, content):
    """insert a question response"""
    userid = int(userid)
    questionid = int(questionid)

    # get current question
    question = get_question(conn, questionid)

    if question is None:
        return

    assert(question.questionid == questionid), 'question.questionid != questionid'

    with conn:
        # add the response to the table
        sql = """
        INSERT INTO responses (
            userid,
            questionid,
            qversion,
            content
        ) VALUES (?, ?, ?, ?);
        """
        params = (userid, questionid, question.qversion, content)
        conn.execute(sql, params)


@catch_db_exceptions
def get_question(conn, questionid):
    """query question content"""
    questionid = int(questionid)

    cur = conn.cursor()
    cur.execute('SELECT * FROM questions WHERE questionid = ?;', (questionid,))
    question = cur.fetchone()
    cur.close()

    if question is None:
        raise ProgrammingError('Non-existant question queried')

    # TODO theres probably a better place for this to live
    Question = namedtuple('Question', question.keys())

    return Question(*question)


@catch_db_exceptions
def get_questions(conn):
    """query all questions"""

    cur = conn.cursor()
    cur.execute('SELECT * FROM questions;')
    questions = cur.fetchall()
    cur.close()

    if questions is None or len(questions) == 0:
        return []

    Question = namedtuple('Question', questions[0].keys())

    return [Question(*q) for q in questions]


@catch_db_exceptions
def get_question_history_all(conn, questionid):
    """query all history for a question"""
    questionid = int(questionid)

    cur = conn.cursor()
    cur.execute('SELECT * FROM question_history WHERE questionid = ?;', (questionid,))
    questions = cur.fetchall()
    cur.close()

    if questions is None or len(questions) == 0:
        return []

    QuestionHistory = namedtuple('QuestionHistory', questions[0].keys())

    return [QuestionHistory(*q) for q in questions]


@catch_db_exceptions
def get_question_history_one(conn, questionid, version=-1):
    """query history for a question of most recent version or specified version"""
    questionid = int(questionid)
    version = -1 if version is None else version

    cur = conn.cursor()
    if version > 0:
        cur.execute("""
            SELECT * FROM question_history
            WHERE questionid = ? AND qversion = ?;""", (questionid, version))
    else:
        cur.execute("""
            SELECT * FROM question_history
            WHERE questionid = ?
            ORDER BY qversion DESC LIMIT 1;""", (questionid,))

    question = cur.fetchone()
    cur.close()

    if question is None:
        raise ProgrammingError('Non-existant question or version queried')

    QuestionHistory = namedtuple('QuestionHistory', question.keys())

    return QuestionHistory(*question)


@catch_db_exceptions
def get_question_responses(conn, questionid):
    """query all question responses"""
    questionid = int(questionid)

    cur = conn.cursor()
    cur.execute('SELECT * FROM responses WHERE questionid = ?;', (questionid,))
    responses = cur.fetchall()
    cur.close()

    if responses is None or len(responses) == 0:
        return []

    Response = namedtuple('Response', responses[0].keys())

    return [Response(*r) for r in responses]


@catch_db_exceptions
def get_users(conn):
    """query all users"""

    cur = conn.cursor()
    cur.execute('SELECT * FROM users;')
    users = cur.fetchall()
    cur.close()

    if users is None or len(users) == 0:
        return []

    Question = namedtuple('User', users[0].keys())

    return [Question(*q) for q in users]
