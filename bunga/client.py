import asyncio
import sys
import os
import threading
import logging
import time
import re

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


class ExecuteCommandError(Exception):

    def __init__(self, output, error):
        self.output = output
        self.error = error


def is_error(text):
    return RE_ERROR.search(text)


def is_warning(text):
    return RE_WARNING.search(text)


class Client(BungaClient):

    def __init__(self, uri, loop):
        super().__init__(uri)
        self._is_connected = False
        self._connected_event = asyncio.Event(loop=loop)
        self._complete_event = asyncio.Event(loop=loop)
        self._fout = None
        self._command_output = []
        self._awaiting_completion = False
        self._error = ''

    async def on_connected(self):
        self._is_connected = True
        self._connected_event.set()

    async def on_disconnected(self):
        self._connected_event.clear()
        self._is_connected = False

        if self._awaiting_completion:
            self._error = 'Connection lost'
            self._complete_event.set()

    def signal_completed(self, error):
        self._awaiting_completion = False
        self._error = error
        self._complete_event.set()

    async def on_execute_command_rsp(self, message):
        if message.output:
            self._command_output.append(message.output)
        else:
            self.signal_completed(message.error)

    async def on_log_entry_ind(self, message):
        pass

    async def on_get_file_rsp(self, message):
        if message.data:
            self._fout.write(message.data)
        else:
            self.signal_completed(message.error)

    async def on_put_file_rsp(self, message):
        self.signal_completed(message.error)

    async def wait_for_connection(self):
        if not self._is_connected:
            await self._connected_event.wait()

    async def execute_command(self, command):
        """Execute given command. Returns the command output as bytes. Raises
        an exception on command failure.

        """

        await self.wait_for_connection()
        self._awaiting_completion = True
        self._command_output = []
        message = self.init_execute_command_req()
        message.command = command
        self._complete_event.clear()
        self.send()
        await self._complete_event.wait()
        output = b''.join(self._command_output)

        if self._error:
            raise ExecuteCommandError(output, self._error)

        return output

    async def get_file(self, remote_path, local_path):
        await self.wait_for_connection()
        self._awaiting_completion = True

        with open(local_path, 'wb') as self._fout:
            message = self.init_get_file_req()
            message.path = remote_path
            self._complete_event.clear()
            self.send()
            await self._complete_event.wait()

        if self._error:
            raise Exception(self._error)

    async def put_file(self, local_path, remote_path):
        await self.wait_for_connection()
        self._awaiting_completion = True
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

        if self._error:
            raise Exception(self._error)


def print_info(text):
    print(cyan(f'[bunga {time.strftime("%H:%M:%S")}] {text}', style='bold'))


def print_error(error):
    print(red(f'ERROR({error})', style='bold'))


def format_log_entry(entry):
    header, text = entry.split(']', 1)
    header += ']'

    mo = RE_ML_LOG.match(text)

    if mo:
        date = mo.group(1)
        level = mo.group(2)
        text = level + mo.group(3) + mo.group(4)

        if level in ['EMERGENCY', 'ALERT', 'CRITICAL', 'ERROR']:
            text = red(text, style='bold')
        elif level == 'WARNING':
            text = yellow(text, style='bold')

        text = yellow(date) + text
    elif is_error(text):
        text = red(text, style='bold')
    elif is_warning(text):
        test = yellow(text, style='bold')

    return green(header) + text


def print_log_entry(entry, fout):
    print(format_log_entry(entry), flush=True, file=fout)


class ClientThread(threading.Thread):

    def __init__(self, uri, client_class=Client):
        super().__init__()
        LOGGER.info('Server URI: %s', uri)
        self._loop = asyncio.new_event_loop()
        self._client = client_class(uri, self._loop)
        self.daemon = True

    def run(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._start())
        self._loop.run_forever()

    def stop(self):
        pass

    def execute_command(self, command):
        return asyncio.run_coroutine_threadsafe(
            self._client.execute_command(command),
            self._loop).result()

    def get_file(self, remote_path, local_path):
        return asyncio.run_coroutine_threadsafe(
            self._client.get_file(remote_path, local_path),
            self._loop).result()

    def put_file(self, local_path, remote_path):
        return asyncio.run_coroutine_threadsafe(
            self._client.put_file(local_path, remote_path),
            self._loop).result()

    async def _start(self):
        self._client.start()


def create_to_path(from_path, to_path):
    if to_path:
        return to_path
    else:
        return os.path.basename(from_path)
