import os

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from ..client import ClientThread


def is_comment(line):
    """Lines starting with "#" are comments.

    """

    return line.strip().startswith('#')


def shell(client):
    commands = [command[1:] for command in []]
    commands.append('exit')
    user_home = os.path.expanduser('~')
    history = FileHistory(os.path.join(user_home, '.bunga-history.txt'))

    while True:
        try:
            line = prompt('$ ',
                          complete_while_typing=True,
                          auto_suggest=AutoSuggestFromHistory(),
                          enable_history_search=True,
                          history=history)
        except EOFError:
            break

        if line:
            if is_comment(line):
                continue

            if line == 'exit':
                break

            try:
                client.execute_command(line)
            except Exception:
                pass


def _do_shell(args):
    client = ClientThread(args.uri)
    client.start()
    shell(client)


def add_subparser(subparsers):
    subparser = subparsers.add_parser('shell')
    subparser.add_argument('-u' ,'--uri',
                           default='tcp://127.0.0.1:28000',
                           help='URI of the server (default: %(default)s)')
    subparser.set_defaults(func=_do_shell)
