import asyncio
import sys
import os
import argparse
import threading

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from .version import __version__
from .bunga_client import BungaClient
from .bunga_pb2 import ExecuteCommandRsp


class Client(BungaClient):

    def __init__(self, uri, loop):
        super().__init__(uri)
        self._execute_command_complete_event = asyncio.Event(loop=loop)

    async def on_connected(self):
        print('Connected to the server.')

    async def on_disconnected(self):
        print("Disconnected from the server.")

    async def on_execute_command_rsp(self, message):
        print(message.output, end='')

        if message.kind == ExecuteCommandRsp.OK:
            print('OK')
            self._execute_command_complete_event.set()
        elif message.kind == ExecuteCommandRsp.ERROR:
            print(f'ERROR({message.error})')
            self._execute_command_complete_event.set()

    async def execute_command(self, command):
        message = self.init_execute_command_req()
        message.command = command
        self._execute_command_complete_event.clear()
        self.send()
        await asyncio.wait_for(self._execute_command_complete_event.wait(), 5)


class ClientThread(threading.Thread):

    def __init__(self, uri):
        super().__init__()
        self._loop = asyncio.new_event_loop()
        self._client = Client(uri, self._loop)
        self.daemon = True

    def run(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._start())
        self._loop.run_forever()

    def execute_command(self, command):
        asyncio.run_coroutine_threadsafe(self._client.execute_command(command),
                                         self._loop).result()

    async def _start(self):
        self._client.start()


def is_comment(line):
    """Lines starting with "#" are comments.

    """

    return line.strip().startswith('#')


def shell(client):
    commands = [command[1:] for command in []]
    commands.append('exit')
    user_home = os.path.expanduser('~')
    history = FileHistory(os.path.join(user_home, '.bunga-history.txt'))

    print("\nWelcome to the Bunga shell.\n")

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
                print()
                print()
                print("Bye!")
                break

            client.execute_command(line)


def do_shell(args):
    client = ClientThread(args.uri)
    client.start()
    shell(client)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--version',
                        action='version',
                        version=__version__,
                        help='Print version information and exit.')

    # Workaround to make the subparser required in Python 3.
    subparsers = parser.add_subparsers(title='subcommands',
                                       dest='subcommand')
    subparsers.required = True

    shell_parser = subparsers.add_parser('shell')
    shell_parser.add_argument('-u' ,'--uri',
                              default='tcp://127.0.0.1:28000',
                              help='URI of the server (default: %(default)s)')
    shell_parser.set_defaults(func=do_shell)

    args = parser.parse_args()

    if args.debug:
        args.func(args)
    else:
        try:
            args.func(args)
        except BaseException as e:
            sys.exit(str(e))


if __name__ == '__main__':
    main()
