# README

## Setup

This project was developed with Python 3.7.5 and pip-19.3.1



##### Installation:
1. `python3 -m venv venv`
1. `. venv/bin/activate`
1. `pip install --upgrade pip`
1. `pip install -r requirements.txt`



##### Configuration:
1. Create a file called `.env` in the project directory (next to `.env-template`). Replace the `DB_NAME` key with a path of your choosing.

    For example:
    ```
    echo DB_PATH="/Users/name/path/to/chatbot_infra/questions.db" > .env
    ```

1. ***Important:*** Before running the CLI, instantiate the database with: `(venv) $ python chatbot_infra/db_setup.py`

1. To run tests: `(venv) $ python -m unittest discover`



##### Run Demo:

A demo is included to interactively illustrate the CLI's functionality.

`(venv) $ python demo.py`



##### CLI Usage

Run the `__main__.py` script as module i.e. `python -m chatbot_infra ...`.

The CLI accepts 10 commands: create_question, update_question, create_user, store_response, get_question, get_questions, get_question_history_all, get_question_history_one, get_question_responses, and get_users.

Usage for each command can be found with `-h` or `--help`: `python -m chatbot_infra get_users --help`

For example, to create a new question, the `create_question` command would be used. The usage is:
```
jpeterson$ python -m chatbot_infra create_question --help
usage: chatbot_infra create_question [-h] [-n NAME] [-t TOPICS] content

positional arguments:
  content                       content of the question to ask

optional arguments:
  -h, --help                    show this help message and exit
  -n NAME, --name NAME          created by name
  -t TOPICS, --topics TOPICS    string list of question topics
```

`content` is mandatory while `name` and `topics` are optional.

`python -m chatbot_infra cq 'this is a question?' -t '[cold,flu,virus]'`



##### CLI Help
```
jpeterson$ python -m chatbot_infra --help
usage: chatbot_infra [-h] [-p PATH]
                     {create_question,cq,update_question,uq,create_user,cu,store_response,sr,get_question,gq,get_questions,gqs,get_question_history_all,gqha,get_question_history_one,gqh,get_question_responses,gqr,get_users,gu}
                     ...

chatbot_infra - Chat Bot Infrastructure command line interface. Append any
command with '--help' for help

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  override path to sqlite3 db file

commands:
  CLI to interact with the DB

  {create_question,cq,update_question,uq,create_user,cu,store_response,sr,get_question,gq,get_questions,gqs,get_question_history_all,gqha,get_question_history_one,gqh,get_question_responses,gqr,get_users,gu}
                                        choose a command to run
    create_question (cq)                create a new question
    update_question (uq)                update an existing question
    create_user (cu)                    create a new user
    store_response (sr)                 store a user's response to a question
    get_question (gq)                   get a question using it's ID
    get_questions (gqs)                 get a list of all questions
    get_question_history_all (gqha)     get the all of the history of a question using it's ID
    get_question_history_one (gqh)      version (or most recent)
    get_question_responses (gqr)        get responses to a question using it's ID
    get_users (gu)                      get all users
```



## Project Description

### a. What went well

In general, the data modeling seemed to go well. I attempted to solve the task using 4 tables: `questions`, `question_history`, `responses`, and `users`.
- `questions` stores the most recent version of each question
- `question_history` has a row for every version of each question including the diff between version updates and the change rationale
- `users` is the table of patients/subjects who are answering the questions in the `questions` table
- `responses` contains the responses to a question from a user

Writing SQL and unit tests, while monotonous, was straightforward and went well. I think was thorough in implementing the required functionality to enable the features specified in the challenge. For example, in `update_question`, the question version is automatically updated and a diff generated from the previous question. Another example is how `responses` tracks which version of the question was answered.

The CLI argparse setup took a lot of boilerplate (and fiddling) but I like the end result. I've never used `add_subparsers` before and found it helpful.

I think the demo is simple and informative.


### b. What was difficult

My biggest problems were: time and a false start with flask.

Earlier, I debated whether or not to use SQLAlchemy and decided against it. I'm afraid that decision may have cost me a lot of time. The `db_setup.py` and `db_api.py` files could have potentially been a lot simpler which would have afforded me more time to work on the UI and more complex interactions in the database. I have only used SQLAlchemy sparingly so I opted for the known (vs. the lesser known). In the end, majority of my time was probably spent on the `db_setup.py` and `db_api.py` files.

This morning, I spent some time fooling around with flask to make a basic HTML form as a UI. Unfortunately, I've only used it a few times and was not confident in my ability to make something in a timely manner so I cut my losses and reverted to a CLI.

### c. What you would improve if you had more time

There is a multitude of things I would do different or improve.

Question topic support is barely included. I had plans to write queries to allow the API to access Question response by type but I ran out of time. Additionally, if SQL had better support for DAGs, representing topics as a hierarchical tree would be worth exploring. More robustly supporting topics is something that I think is very important but it's not included.

The python diff library doesn't do a good job of highlighting what changed if the question is short. I'd like to investigate that further since it seemed central to the challenge prompt. Additionally, I'd like to allow the user to specify which versions of a question to diff.

I think it would be cool to create classes for the major entities (question, response, etc) who's constructor accepts the results I'm currently using. (i.e a factory from the `namedtuple` result objects) This would be useful for abstracting the business logic away from db and for templates if in a future version a web UI was used.

I didn't have time to analyze query plans and optimize by creating indexes. I'm sure there are opportunities for improvement there.

### Discussion

> For later discussion, think about the features of conversation topics that make some topics more or less relevant to other topics and how you might organize this information. We will ask for your insights later.

Questions are currently standalone entities. In reality, they are part of a much bigger knowledge system. Questions would have to have features that allow them to be associated with which topic is the most relevant to the patient's care. For example, if the chief compliant in a patient of a certain age and sex is stomach ache, the system could create a model that tries to explain the chief complaint. The model could be a log regression where the question topics are features. The system could recommend question topics by greedily selecting unanswered topics.

