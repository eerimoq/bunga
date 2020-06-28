import re
import sys
import os
import subprocess

import prompt_toolkit
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.patch_stdout import patch_stdout

from ..client import Client
from ..client import ClientThread
from ..client import print_info
from ..client import print_error
from ..client import format_log_entry
from ..client import NotConnectedError
from ..client import ExecuteCommandError
from .. import __version__


RE_COMMAND = re.compile(r'^\s*(\S+)', re.MULTILINE)


class ShellClient(Client):

    async def on_disconnected(self):
        if self._is_connected:
            print_info('Disconnected')

        await super().on_disconnected()

    async def on_connect_rsp(self, message):
        await super().on_connect_rsp(message)
        print_info('Connected')


def is_comment(line):
    """Lines starting with "#" are comments.

    """

    return line.strip().startswith('#')


def print_output(output, pipe_commands):
    if pipe_commands:
        with subprocess.Popen(pipe_commands,
                              shell=True,
                              stdin=subprocess.PIPE,
                              encoding='utf-8') as proc:
            print(output, end='', flush=True, file=proc.stdin)
    else:
        print(output, end='', flush=True)


def parse_command(line):
    """Split given line in command to execute on the remote system and
    commands to pipe/redirect the output to on the host.

    Pipe:

    "ll | grep foo" -> ('ll', 'grep foo')

    Redirect:

    "cat /root/conf > conf" -> ('cat /root/conf', 'cat > conf')

    Pipe found first, redirect part of host command:

    "ll | grep foo > log" -> ('ll', 'grep foo > log')

    """

    pipe_command, _, pipe_commands = line.partition('|')
    redirect_command, _, redirect_commands = line.partition('>')

    pipe_command = pipe_command.strip()
    pipe_commands = pipe_commands.strip()
    redirect_command = redirect_command.strip()
    redirect_commands = redirect_commands.strip()

    if len(pipe_command) <= len(redirect_command):
        command = pipe_command
    else:
        command = redirect_command
        pipe_commands = f'cat > {redirect_commands}'

    return (command, pipe_commands)


def execute_command(client, command):
    return client.execute_command(command).decode('utf-8', 'replace')


def execute_dmesg(client):
    lines = []

    for line in execute_command(client, 'dmesg').splitlines():
        lines.append(format_log_entry(line))

    return '\n'.join(lines) + '\n'


def load_commands(client):
    commands = [
        'netstat',
        'uptime',
        'ps',
        'dmesg'
    ]

    client.wait_for_connection()
    output = execute_command(client, 'help')
    output = output.split('\nCommands\n')[1]

    for line in output.splitlines():
        mo = RE_COMMAND.match(line)

        if mo:
            commands.append(mo.group(1))

    return sorted(list(set(commands)))


def shell_main(client):
    user_home = os.path.expanduser('~')
    history = FileHistory(os.path.join(user_home, '.bunga-history.txt'))
    commands = load_commands(client)

    while True:
        try:
            line = prompt_toolkit.prompt(ANSI('\x1b[36m(bunga)\x1b[0m '),
                                         completer=FuzzyWordCompleter(commands),
                                         complete_while_typing=True,
                                         auto_suggest=AutoSuggestFromHistory(),
                                         enable_history_search=True,
                                         complete_style=CompleteStyle.READLINE_LIKE,
                                         history=history)
        except EOFError:
            break

        if line:
            if is_comment(line):
                continue

            if line == 'exit':
                break

            command, pipe_commands = parse_command(line)

            try:
                if command == 'dmesg':
                    output = execute_dmesg(client)
                else:
                    output = execute_command(client, command)

                print_output(output, pipe_commands)
            except ExecuteCommandError as e:
                print(e.output.decode('utf-8', 'replace'), end='')
                print_error(e.error)
            except NotConnectedError:
                print_error('Not connected.')


def _do_shell(args):
    print_info(f'bunga {__version__}')
    client = ClientThread(args.uri, ShellClient)
    client.start()

    with patch_stdout():
        shell_main(client)


def add_subparser(subparsers):
    subparser = subparsers.add_parser('shell')
    subparser.add_argument('-u' ,'--uri',
                           default='tcp://127.0.0.1:28000',
                           help='URI of the server (default: %(default)s)')
    subparser.set_defaults(func=_do_shell)
