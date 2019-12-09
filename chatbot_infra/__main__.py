#!/usr/bin/env python3
"""
ChatBot Infrastructure

Created by: Jeff Peterson 8 Dec 2019
"""

from chatbot_infra.cli import get_cli_args, execute_cli_command
from chatbot_infra.utils import get_db_conn


if __name__ == '__main__':

    args = get_cli_args()

    conn = get_db_conn(path=args.path)

    # connect the CLI to the database api
    execute_cli_command(args, conn)

    conn.close()
