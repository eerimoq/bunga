import os

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from ..client import Client
from ..client import ClientThread
from ..client import print_info
from ..client import print_error
from ..client import print_log_entry
from ..client import ExecuteCommandError


class ShellClient(Client):

    async def on_connected(self):
        await super().on_connected()
        print_info('Connected')

    async def on_disconnected(self):
        await super().on_disconnected()
        print_info('Disconnected')


def is_comment(line):
    """Lines starting with "#" are comments.

    """

    return line.strip().startswith('#')


def print_output(command, output):
    if command == 'dmesg':
        for line in output.splitlines():
            print_log_entry(line)
    else:
        print(output, end='', flush=True)


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
                output = client.execute_command(line)
                print_output(line, output)
            except ExecuteCommandError as e:
                print_error(e.error)


def _do_shell(args):
    client = ClientThread(args.uri, ShellClient)
    client.start()
    shell(client)


def add_subparser(subparsers):
    subparser = subparsers.add_parser('shell')
    subparser.add_argument('-u' ,'--uri',
                           default='tcp://127.0.0.1:28000',
                           help='URI of the server (default: %(default)s)')
    subparser.set_defaults(func=_do_shell)
