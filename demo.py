#!/usr/bin/env python3
"""
ChatBot Infrastructure CLI Demo
Please see the README.md for more information

Created by: Jeff Peterson 8 Dec 2019
"""

import subprocess
from time import sleep


class color:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_wait(s, t=3):
    print(s)
    sleep(t)


def call_print_wait(*a, t=3, **kwa):
    print(color.RED + '>>> ' + ' '.join(a[0]) + color.ENDC)
    output = subprocess.check_output(*a, **kwa)

    if output:
        output = output.decode('utf-8').strip()
        print_wait(color.GREEN + output + color.ENDC)

    sleep(t)
    return output


prefix = ['python', '-m', 'chatbot_infra']


print_wait('\nWelcome to the ChatBot Infrastructure CLI Demo...\n', t=2)
print_wait('The CLI exposes all the current functionality in the database API')

print_wait(
    color.RED +
    'Please ensure that the python `db_setup.py` script has been run before you begin.' +
    color.ENDC)

print()
print_wait('First we are going to create a few users to respond to questions')
print_wait('Users are created with the `create_user` command (alias: `cu`)')
print_wait('For example: we are going to create a user named Bob')
uid1 = call_print_wait(prefix + ['create_user', 'Bob', '--email', 'bob@example.com'])

print_wait('Enter another name:')
name = input()
uid2 = call_print_wait(prefix + ['cu', name], t=1)


print()
print_wait('Next, we are going to create a few questions')
print_wait('Questions are created with the `create_question` command (alias: `cq`)')
call_print_wait(
    prefix +
    ['create_question', '"This is a question about your health and wellbeing?"'])
print()
print_wait('Questions can also have topics. Topics are represented as a list.')
call_print_wait(prefix + ['cq', '"This is a question two"', '-t', '[flu,virus,cold]'])
print()
print_wait('One more question...')
qid = call_print_wait(prefix + ['cq', '"THis is a questino where we ahve made a few errors?"'])

print()
print_wait('That last question contains some serious errors. We need to update it.')
print_wait('Questions are updated with the `update_question` command (alias: `uq`)')
print_wait('Questions updates can have a rationale to track the reason for the change')
call_print_wait(prefix + [
    'uq',
    str(qid),
    '"This is a question where we have made no errors?"',
    '-r', '"Fixing several spelling mistakes"'
])

print()
print_wait('Now that we\'ve updated a question, let\'s view the questions history')
print_wait('Questions history is queried with the `get_question_hist` command (alias: `gqh`)')
call_print_wait(prefix + ['gqh', str(qid)], t=4)
print_wait('We can see the diff between the previous question version and the current version')

print()
print_wait('Finally, let\'s add a question response from a user.')
print_wait('Responses are created with the `store_response` command (alias: `sr`)')
call_print_wait(prefix + ['sr', str(uid1), str(qid), '"This is a reponse to a question"'])
call_print_wait(prefix + ['sr', str(uid2), str(qid), '"Another reponse to the question"'])

print()
print_wait('Responses are viewed with `get_question_responses` command (alias: `gqr`)')
call_print_wait(prefix + ['gqr', str(qid)])


print()
print('Other available commands are:')
print('    `get_questions` (alias: `gqs`)')
print('    `get_users` (alias: `gu`)')


print_wait('\nThanks for using the CLI demo!\n')
