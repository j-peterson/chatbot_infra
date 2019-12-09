"""
ChatBot Infrastructure CLI

Created by: Jeff Peterson 8 Dec 2019
"""

import argparse
import chatbot_infra.db_api as db


def get_cli_args():
    """setup CLI argument parser"""

    parser = argparse.ArgumentParser(
        prog='chatbot_infra',
        description="""chatbot_infra - Chat Bot Infrastructure command line interface.
        Append any command with '--help' for help""")
    parser.add_argument('-p', '--path', help='override path to sqlite3 db file')

    # CLI

    subparsers = parser.add_subparsers(
        title='commands',
        dest='command',
        description='CLI to interact with the DB',
        help='choose a command to run')

    # create a parser for the 'create_question' command
    sp_create_question = subparsers.add_parser(
        'create_question',
        aliases=['cq'],
        help='create a new question')
    sp_create_question.add_argument('content', help='content of the question to ask')
    sp_create_question.add_argument('-n', '--name', help='created by name')
    sp_create_question.add_argument('-t', '--topics', help='string list of question topics')

    # create a parser for the 'update_question' command
    sp_update_question = subparsers.add_parser(
        'update_question',
        aliases=['uq'],
        help='update an existing question')
    sp_update_question.add_argument('questionid', help='questionid of the question to update')
    sp_update_question.add_argument('content', help='content of the new question')
    sp_update_question.add_argument('-n', '--name', help='created by name')
    sp_update_question.add_argument('-c', '--createdby', help='createdby for the change')
    sp_update_question.add_argument('-r', '--rationale', help='rationale for the change')

    # create a parser for the 'create_user' command
    sp_create_user = subparsers.add_parser(
        'create_user',
        aliases=['cu'],
        help='create a new user')
    sp_create_user.add_argument('name', help='name of the new user')
    sp_create_user.add_argument('--email', help='email')
    sp_create_user.add_argument('--phone', help='phone')
    sp_create_user.add_argument('--birthsex', help='birthsex')
    sp_create_user.add_argument('--pronouns', help='pronouns')

    # create a parser for the 'store_response' command
    sp_store_response = subparsers.add_parser(
        'store_response',
        aliases=['sr'],
        help='store a user\'s response to a question')
    sp_store_response.add_argument('userid', help='userid of the responder')
    sp_store_response.add_argument('questionid', help='questionid of the question to update')
    sp_store_response.add_argument('content', help='content of the response')

    # create a parser for the 'get_question' command
    sp_get_question = subparsers.add_parser(
        'get_question',
        aliases=['gq'],
        help='get a question using it\'s ID')
    sp_get_question.add_argument('questionid', help='questionid of the question to retreive')

    # create a parser for the 'get_questions' command
    subparsers.add_parser(
        'get_questions',
        aliases=['gqs'],
        help='get a list of all questions')

    # create a parser for the 'get_question_history_all' command
    sp_get_q_hist_all = subparsers.add_parser(
        'get_question_history_all',
        aliases=['gqha'],
        help='get the all of the history of a question using it\'s ID')
    sp_get_q_hist_all.add_argument('questionid', help='questionid of the question to retreive')

    # create a parser for the 'get_question_history_one' command
    sp_get_q_hist_all = subparsers.add_parser(
        'get_question_history_one',
        aliases=['gqh'],
        help='get the history of a question using it\'s ID and version (or most recent)')
    sp_get_q_hist_all.add_argument('questionid', help='questionid of the question to retreive')
    sp_get_q_hist_all.add_argument('-q', '--qversion', help='question version of the q to retreive')

    # create a parser for the 'get_question_responses' command
    sp_get_question_res = subparsers.add_parser(
        'get_question_responses',
        aliases=['gqr'],
        help='get responses to a question using it\'s ID')
    sp_get_question_res.add_argument('questionid', help='questionid of the question to retreive')

    # create a parser for the 'get_users' command
    subparsers.add_parser(
        'get_users',
        aliases=['gu'],
        help='get all users')

    # after configuring the CLI, parse the input args
    return parser.parse_args()


def execute_cli_command(args, conn):
    """envoke the command specified in args using db conn
    args - namespace return value from parse.parse_args
    conn - database connection from utils.get_db_conn for use in db_api
    """

    if args.command in ['create_question', 'cq']:
        qid = db.create_question(conn, args.content, createdby=args.name, topics=args.topics)
        print(qid)

    if args.command in ['update_question', 'uq']:
        db.update_question(
            conn,
            args.questionid,
            args.content,
            createdby=args.createdby,
            rationale=args.rationale)

    if args.command in ['create_user', 'cu']:
        userid = db.create_user(
            conn,
            args.name,
            email=args.email,
            phone=args.phone,
            birthsex=args.birthsex,
            pronouns=args.pronouns)
        print(userid)

    if args.command in ['store_response', 'sr']:
        db.store_response(conn, args.userid, args.questionid, args.content)

    if args.command in ['get_question', 'gq']:
        question = db.get_question(conn, args.questionid)
        print(question)

    if args.command in ['get_questions', 'gqs']:
        question_list = db.get_questions(conn)
        for q in question_list:
            print(q)

    if args.command in ['get_question_history_all', 'gqha']:
        question_list = db.get_question_history_all(conn, args.questionid)
        for q in question_list:
            print(q)

    if args.command in ['get_question_history_one', 'gqh']:
        question = db.get_question_history_one(conn, args.questionid, args.qversion)
        print('historyid: {}'.format(question.historyid))
        print('questionid: {}'.format(question.questionid))
        print('qversion: {}'.format(question.qversion))
        print('content: {}'.format(question.content))
        print('contentdiff: \n{}'.format(question.contentdiff))
        print('createdat: {}'.format(question.createdat))
        print('createdby: {}'.format(question.createdby))
        print('rationale: {}'.format(question.rationale))

    if args.command in ['get_question_responses', 'gqr']:
        responses_list = db.get_question_responses(conn, args.questionid)
        for r in responses_list:
            print(r)

    if args.command in ['get_users', 'gu']:
        users_list = db.get_users(conn)
        for u in users_list:
            print(u)
