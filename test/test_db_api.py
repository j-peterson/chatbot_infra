import unittest

from chatbot_infra.utils import get_db_conn
from chatbot_infra.db_setup import db_setup
import chatbot_infra.db_api as db


class Test_create_question(unittest.TestCase):

    def setUp(self):
        self.conn = get_db_conn(path=':memory:')
        db_setup(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_create_question(self):
        """test_create_question the golden path"""

        # first create new question and question history
        content = 'test question content?'
        db.create_question(self.conn, content)

        # sanity check questions table
        with self.conn:
            results = list(self.conn.execute('SELECT * FROM questions;'))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['content'], content)

        question_id = results[0]['questionid']

        # sanity check question_history table
        with self.conn:
            results = list(self.conn.execute('SELECT * FROM question_history;'))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['questionid'], question_id)
        self.assertEqual(results[0]['content'], content)


class Test_makediff(unittest.TestCase):

    def test_simpleDiff(self):
        diff = db._makediff('This is the the old question?  foo\n', 'This is the new question?\n')
        answer = [
            '- This is the the old question?  foo\n',
            '?             ^^ ^^^^          -----\n',
            '+ This is the new question?\n',
            '?             ^ ^\n']

        self.assertEqual(diff, ''.join(answer))

    def test_add_newline(self):
        diff = db._makediff('This is the the old question?  foo', 'This is the new question?')
        answer = [
            '- This is the the old question?  foo\n',
            '?             ^^ ^^^^          -----\n',
            '+ This is the new question?\n',
            '?             ^ ^\n']

        self.assertEqual(diff, ''.join(answer))


class Test_update_question(unittest.TestCase):

    def setUp(self):
        self.conn = get_db_conn(path=':memory:')
        db_setup(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_update_question(self):
        """test_update_question golden path"""

        # first create a question which we will later update
        content = 'test question content?'
        db.create_question(self.conn, content)

        # second update the new question
        new_content = 'test updated content here?'
        rationale = 'question was unclear'
        createdby = 'jeff'
        db.update_question(self.conn, 1, new_content, createdby=createdby, rationale=rationale)

        # sanity check update to questions
        with self.conn:
            results = list(self.conn.execute('SELECT * FROM questions;'))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['qversion'], 2)
        self.assertEqual(results[0]['content'], new_content)

        # sanity check update to question_history
        with self.conn:
            results = list(self.conn.execute('SELECT * FROM question_history;'))

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['qversion'], 1)
        self.assertEqual(results[1]['qversion'], 2)
        self.assertEqual(results[1]['createdby'], createdby)
        self.assertEqual(results[1]['rationale'], rationale)


class Test_create_user(unittest.TestCase):

    def setUp(self):
        self.conn = get_db_conn(path=':memory:')
        db_setup(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_create_user(self):
        """test_create_user golden path"""

        # first create a question which we will later update
        name = 'jeff'

        db.create_user(self.conn, name)

        # sanity check update to questions
        with self.conn:
            results = list(self.conn.execute('SELECT * FROM users;'))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], name)


class Test_store_response(unittest.TestCase):

    def setUp(self):
        self.conn = get_db_conn(path=':memory:')
        db_setup(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_store_response(self):
        """test_store_response golden path"""

        # first create a user and a question
        db.create_user(self.conn, 'Mr. Foo Bar III')
        db.create_question(self.conn, 'test question content?')

        userid = 1   # we cheat and know the generated IDs are 1
        questionid = 1
        content = 'answer answer answer'

        db.store_response(self.conn, userid, questionid, content)

        # sanity check update to questions
        with self.conn:
            results = list(self.conn.execute('SELECT * FROM responses;'))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['content'], content)


class Test_get_questions(unittest.TestCase):

    def setUp(self):
        self.conn = get_db_conn(path=':memory:')
        db_setup(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_get_questions(self):
        """get_questions golden path"""

        # first create a few questions
        db.create_question(self.conn, 'test question content?')
        db.create_question(self.conn, 'test test test')
        db.create_question(self.conn, 'foo')

        # get those questions
        questions = db.get_questions(self.conn)

        self.assertEqual(len(questions), 3)
        self.assertEqual(questions[0].content, 'test question content?')
        self.assertEqual(questions[1].content, 'test test test')
        self.assertEqual(questions[2].content, 'foo')


class Test_get_question_history_all(unittest.TestCase):

    def setUp(self):
        self.conn = get_db_conn(path=':memory:')
        db_setup(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_get_question_history_all(self):
        """get_question_history_all golden path"""

        # first create a few question
        qid = db.create_question(self.conn, 'test question content?')

        # update the question
        content = 'blah blah blah blah blah blah'
        createdby = 'jeff'
        rationale = 'update because wrong'
        db.update_question(self.conn, qid, content, createdby=createdby, rationale=rationale)

        content = 'blah blah blah blah blah blah now correct'
        createdby = 'jeff clone'
        rationale = 'This is the perfect question'
        db.update_question(self.conn, qid, content, createdby=createdby, rationale=rationale)

        # finally get history
        question_hist = db.get_question_history_all(self.conn, qid)

        self.assertEqual(len(question_hist), 3)
        self.assertEqual(question_hist[0].content, 'test question content?')


class Test_get_question_history_one(unittest.TestCase):

    def setUp(self):
        self.conn = get_db_conn(path=':memory:')
        db_setup(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_get_question_history_one(self):
        """get_question_history_one golden path"""

        # first create a few question
        qid = db.create_question(self.conn, 'test question content?')

        # update the question
        db.update_question(self.conn, qid, 'blah blah blah blah blah blah')
        db.update_question(self.conn, qid, 'blah blam blah blah blah blah now correct')

        # finally get history of last question
        question_hist_last = db.get_question_history_one(self.conn, qid)
        self.assertEqual(question_hist_last.qversion, 3)
        self.assertEqual(question_hist_last.content, 'blah blam blah blah blah blah now correct')

        # finally get history of specific question version
        question_hist_last = db.get_question_history_one(self.conn, qid, 2)
        self.assertEqual(question_hist_last.qversion, 2)
        self.assertEqual(question_hist_last.content, 'blah blah blah blah blah blah')


if __name__ == '__main__':
    unittest.main()
