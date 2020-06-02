import asyncio
import sys
import os
import argparse
import threading
import logging
import time
import re

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from colors import red
from colors import yellow
from colors import green
from colors import cyan

from .version import __version__
from .bunga_client import BungaClient


LOGGER = logging.getLogger(__file__)

RE_ML_LOG = re.compile(r'([\d\- 0-9:]+)(\w+)( \w+)(.*)')
RE_ERROR = re.compile(r'error', re.IGNORECASE)
RE_WARNING = re.compile(r'warning', re.IGNORECASE)


def print_info(text):
    print(cyan(f'[bunga {time.strftime("%H:%M:%S")}] {text}', style='bold'))


def is_error(text):
    return RE_ERROR.search(text)


def is_warning(text):
    return RE_WARNING.search(text)


def print_log_entry(header, text):
    mo = RE_ML_LOG.match(text)

    if mo:
        date = mo.group(1)
        text = mo.group(2) + mo.group(3) + mo.group(4)

        if mo.group(2) == 'ERROR':
            text = red(text, style='bold')
        elif mo.group(2) == 'WARNING':
            text = yellow(text, style='bold')

        text = yellow(date) + text
    elif is_error(text):
        text = red(text, style='bold')
    elif is_warning(text):
        test = yellow(text, style='bold')

    print(green(header), text, flush=True)


class Client(BungaClient):

    def __init__(self, uri, loop):
        super().__init__(uri)
        self._is_connected = False
        self._connected_event = asyncio.Event(loop=loop)
        self._complete_event = asyncio.Event(loop=loop)
        self._fout = None
        self._command_output = []
        self._error = ''
        self.print_log_entries = False

    async def on_connected(self):
        print_info('Connected')
        self._is_connected = True
        self._connected_event.set()

    async def on_disconnected(self):
        print_info('Disconnected')
        self._connected_event.clear()
        self._is_connected = False
        self._complete_event.set()

    def print_result_and_signal(self, error):
        if error:
            print(red(f'ERROR({error})', style='bold'))

        self._error = error
        self._complete_event.set()

    async def on_execute_command_rsp(self, message):
        if message.output:
            print(message.output, end='', flush=True)
            self._command_output.append(message.output)
        else:
            self.print_result_and_signal(message.error)

    async def on_log_entry_ind(self, message):
        if self.print_log_entries:
            print_log_entry(message.text[0], message.text[1])

    async def on_get_file_rsp(self, message):
        if message.data:
            self._fout.write(message.data)
        else:
            self.print_result_and_signal(message.error)

    async def on_put_file_rsp(self, message):
        self.print_result_and_signal(message.error)

    async def execute_command(self, command):
        if not self._is_connected:
            await self._connected_event.wait()

        self._command_output = []
        message = self.init_execute_command_req()
        message.command = command
        self._complete_event.clear()
        self.send()
        await self._complete_event.wait()

        return (''.join(self._command_output), self._error)

    async def get(self, remote_path, local_path):
        if not self._is_connected:
            await self._connected_event.wait()

        with open(local_path, 'wb') as self._fout:
            message = self.init_get_file_req()
            message.path = remote_path
            self._complete_event.clear()
            self.send()
            await self._complete_event.wait()

        return self._error

    async def put(self, local_path, remote_path):
        if not self._is_connected:
            await self._connected_event.wait()

        self._complete_event.clear()

        with open(local_path, 'rb') as fin:
            message = self.init_put_file_req()
            message.path = remote_path
            self.send()

            while True:
                message = self.init_put_file_req()
                message.data = fin.read(64)
                self.send()

                if not message.data:
                    break

        await self._complete_event.wait()

        return self._error


class ClientThread(threading.Thread):

    def __init__(self, uri, print_log_entries=False):
        super().__init__()
        LOGGER.info('Server URI: %s', uri)
        self._loop = asyncio.new_event_loop()
        self._client = Client(uri, self._loop)
        self._client.print_log_entries = print_log_entries
        self.daemon = True

    def run(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._start())
        self._loop.run_forever()

    def execute_command(self, command):
        asyncio.run_coroutine_threadsafe(self._client.execute_command(command),
                                         self._loop).result()

    def get(self, remote_path, local_path):
        asyncio.run_coroutine_threadsafe(self._client.get(remote_path, local_path),
                                         self._loop).result()

    def put(self, local_path, remote_path):
        asyncio.run_coroutine_threadsafe(self._client.put(local_path, remote_path),
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

            client.execute_command(line)


def create_to_path(from_path, to_path):
    if to_path:
        return to_path
    else:
        return os.path.basename(from_path)


def do_shell(args):
    client = ClientThread(args.uri)
    client.start()
    shell(client)


def do_put(args):
    client = ClientThread(args.uri)
    client.start()
    remotefile = create_to_path(args.localfile, args.remotefile)
    client.put(args.localfile, remotefile)


def do_get(args):
    client = ClientThread(args.uri)
    client.start()
    localfile = create_to_path(args.remotefile, args.localfile)
    client.get(args.remotefile, localfile)


def do_log(args):
    client = ClientThread(args.uri, print_log_entries=True)
    client.start()

    while True:
        time.sleep(100)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-l', '--log-level',
                        default='error',
                        choices=[
                            'debug', 'info', 'warning', 'error', 'critical'
                        ],
                        help='Set the logging level (default: %(default)s).')
    parser.add_argument('--version',
                        action='version',
                        version=__version__,
                        help='Print version information and exit.')

    # Workaround to make the subparser required in Python 3.
    subparsers = parser.add_subparsers(title='subcommands',
                                       dest='subcommand')
    subparsers.required = True

    # The shell subparser.
    shell_parser = subparsers.add_parser('shell')
    shell_parser.add_argument('-u' ,'--uri',
                              default='tcp://127.0.0.1:28000',
                              help='URI of the server (default: %(default)s)')
    shell_parser.set_defaults(func=do_shell)

    # The put subparser.
    put_parser = subparsers.add_parser('put')
    put_parser.add_argument('-u' ,'--uri',
                            default='tcp://127.0.0.1:28000',
                            help='URI of the server (default: %(default)s)')
    put_parser.add_argument('localfile', help='The local file path.')
    put_parser.add_argument('remotefile',
                            nargs='?',
                            help='The remote file path.')
    put_parser.set_defaults(func=do_put)

    # The get subparser.
    get_parser = subparsers.add_parser('get')
    get_parser.add_argument('-u' ,'--uri',
                            default='tcp://127.0.0.1:28000',
                            help='URI of the server (default: %(default)s)')
    get_parser.add_argument('remotefile', help='The remote file path.')
    get_parser.add_argument('localfile',
                            nargs='?',
                            help='The local file path.')
    get_parser.set_defaults(func=do_get)

    # The log subparser.
    log_parser = subparsers.add_parser('log')
    log_parser.add_argument('-u' ,'--uri',
                            default='tcp://127.0.0.1:28000',
                            help='URI of the server (default: %(default)s)')
    log_parser.set_defaults(func=do_log)

    args = parser.parse_args()

    level = logging.getLevelName(args.log_level.upper())
    logging.basicConfig(level=level, format='%(asctime)s %(message)s')

    if args.debug:
        args.func(args)
    else:
        try:
            args.func(args)
        except BaseException as e:
            sys.exit(str(e))


if __name__ == '__main__':
    main()
