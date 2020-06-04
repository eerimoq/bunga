import sys
import os
import subprocess

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from ..client import Client
from ..client import ClientThread
from ..client import print_info
from ..client import print_error
from ..client import print_log_entry
from ..client import ExecuteCommandError
from .. import linux

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


def fprint_output(command, output, fout):
    if command.startswith('dmesg'):
        for line in output.splitlines():
            print_log_entry(line, fout)
    else:
        print(output, end='', flush=True, file=fout)


def print_output(command, pipe_commands, output):
    if pipe_commands:
        with subprocess.Popen(pipe_commands,
                              shell=True,
                              stdin=subprocess.PIPE,
                              encoding='utf-8') as proc:
            fprint_output(command, output, proc.stdin)
    else:
        fprint_output(command, output, sys.stdout)


def parse_command(line):
    """Split given line in command to execute on the remote system and
    commands to pipe/redirect the output to on the host.

    Pipe:

    "ls | grep foo" -> ('ls', 'grep foo')

    Redirect:

    "cat /root/conf > conf" -> ('cat /root/conf', 'cat > conf')

    Pipe found first, redirect part of host command:

    "ls | grep foo > log" -> ('ls', 'grep foo > log')

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


def shell_main(client):
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

            command, pipe_commands = parse_command(line)

            if command == 'netstat':
                commands = ['cat /proc/net/tcp']
                formatter = linux.format_netstat
            elif command == 'uptime':
                commands = ['cat /proc/uptime', 'cat /proc/loadavg']
                formatter = linux.format_uptime
            else:
                commands = [command]
                formatter = lambda output: output

            try:
                output = []

                for command in commands:
                    output.append(client.execute_command(command))

                print_output(command, pipe_commands, formatter(*output))
            except ExecuteCommandError as e:
                print(e.output, end='')
                print_error(e.error)


def _do_shell(args):
    client = ClientThread(args.uri, ShellClient)
    client.start()

    shell_main(client)


def add_subparser(subparsers):
    subparser = subparsers.add_parser('shell')
    subparser.add_argument('-u' ,'--uri',
                           default='tcp://127.0.0.1:28000',
                           help='URI of the server (default: %(default)s)')
    subparser.set_defaults(func=_do_shell)
