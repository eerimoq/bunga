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
from colors import color

from .version import __version__
from .bunga_client import BungaClient
from . import linux


LOGGER = logging.getLogger(__file__)

RE_ML_LOG = re.compile(r'( \d+-\d+-\d+ \d+:\d+:\d+)( [^ ]+)( [^ ]+)(.*)')
RE_ERROR = re.compile(r'error', re.IGNORECASE)
RE_WARNING = re.compile(r'warning', re.IGNORECASE)


class CompletionError(Exception):

    def __init__(self, error):
        self.error = error


class NotConnectedError(Exception):

    pass


class ExecuteCommandError(Exception):

    def __init__(self, output, error):
        self.output = output
        self.error = error


class GetFileError(Exception):

    def __init__(self, remote_path, error):
        self.remote_path = remote_path
        self.error = error

    def __str__(self):
        return f"Failed to get '{self.remote_path}' with error '{self.error}'."


class PutFileError(Exception):

    def __init__(self, remote_path, error):
        self.remote_path = remote_path
        self.error = error

    def __str__(self):
        return f"Failed to put '{self.remote_path}' with error '{self.error}'."


class Progress:

    def init(self, size):
        pass

    def update(self, size):
        pass


def is_error(text):
    return RE_ERROR.search(text)


def is_warning(text):
    return RE_WARNING.search(text)


class Client(BungaClient):

    def __init__(self,
                 uri,
                 loop,
                 connection_refused_delay=1,
                 connect_timeout_delay=0):
        super().__init__(uri)
        self._is_connected = False
        self._connected_event = asyncio.Event(loop=loop)
        self._complete_queue = asyncio.Queue(loop=loop)
        self._fget = None
        self._get_file_size = None
        self._get_progress = None
        self._command_output = []
        self._connect_exception = None
        self._connection_refused_delay = connection_refused_delay
        self._connect_timeout_delay = connect_timeout_delay
        self._maximum_message_size = 64
        self._ps_formatter = linux.PsFormatter()

    async def on_connected(self):
        self.init_connect_req()
        self.send()

    async def on_disconnected(self):
        if self._is_connected:
            self._connected_event.clear()
            self._is_connected = False
            await self._complete_queue.put(('Connection lost.', None))
        else:
            await asyncio.sleep(1)


    async def on_connect_failure(self, exception):
        if isinstance(exception, ConnectionRefusedError):
            delay = self._connection_refused_delay
        else:
            delay = self._connect_timeout_delay

        if delay is None:
            self._connect_exception = exception
            self._connected_event.set()

        return delay

    async def _write_completed(self, message):
        await self._complete_queue.put((message.error, message))

    async def _wait_for_completion(self):
        error, message = await self._complete_queue.get()

        if error:
            raise CompletionError(error)

        return message

    def _clear_completion_queue(self):
        while not self._complete_queue.empty():
            self._complete_queue.get_nowait()

    async def _send_and_wait_for_completion(self):
        if not self._is_connected:
            raise NotConnectedError()

        self._clear_completion_queue()
        self.send()

        return await self._wait_for_completion()

    async def on_connect_rsp(self, message):
        # ToDo: Use received keep alive timeout.
        if message.maximum_message_size > 64:
            self._maximum_message_size = message.maximum_message_size

        self._is_connected = True
        self._connect_exception = None
        self._connected_event.set()

    async def on_execute_command_rsp(self, message):
        if message.output:
            self._command_output.append(message.output)
        else:
            await self._write_completed(message)

    async def on_log_entry_ind(self, message):
        pass

    async def _on_get_file_rsp_open(self, message):
        if message.size > 0:
            self._get_file_size = message.size
            self._get_progress.init(message.size)
        else:
            self._fget = None
            await self._write_completed(message)

    async def _on_get_file_rsp_data(self, message):
        self._fget.write(message.data)
        self._get_progress.update(len(message.data))
        message = self.init_get_file_req()
        message.acknowledge_count = 1
        self.send()

    async def _on_get_file_rsp_close(self, message):
        self._fget = None
        await self._write_completed(message)

    async def on_get_file_rsp(self, message):
        if self._fget is None:
            return

        if self._get_file_size is None:
            await self._on_get_file_rsp_open(message)

        if message.data:
            await self._on_get_file_rsp_data(message)
        else:
            await self._on_get_file_rsp_close(message)

    async def on_put_file_rsp(self, message):
        await self._write_completed(message)

    async def wait_for_connection(self, timeout=None):
        if not self._is_connected:
            await asyncio.wait_for(self._connected_event.wait(), timeout)

            if self._connect_exception:
                raise self._connect_exception

    async def execute_command_netstat(self):
        output = await self.execute_command('cat /proc/net/tcp')

        return linux.format_netstat(output.decode()).encode()

    async def execute_command_uptime(self):
        proc_uptime = await self.execute_command('cat /proc/uptime')
        proc_loadavg = await self.execute_command('cat /proc/loadavg')

        return linux.format_uptime(proc_uptime.decode(),
                                   proc_loadavg.decode()).encode()

    async def execute_command_ps(self):
        """This is a ps command for Monolinux, only showing information for
        the init process and its threads. Make it more general at some
        point?

        """

        proc_n_stat = []
        proc_1_task = await self.execute_command('ls /proc/1/task')

        for pid in proc_1_task.split():
            output = await self.execute_command(
                f'cat /proc/1/task/{pid.decode()}/stat')
            proc_n_stat.append(output.decode())

        proc_stat = await self.execute_command('cat /proc/stat')

        return self._ps_formatter.format(proc_stat.decode(), proc_n_stat).encode()

    async def execute_command(self, command):
        """Execute given command. Returns the command output as bytes. Raises
        an exception on command failure.

        """

        if command == 'netstat':
            return await self.execute_command_netstat()
        elif command == 'uptime':
            return await self.execute_command_uptime()
        elif command == 'ps':
            return await self.execute_command_ps()

        self._command_output = []
        message = self.init_execute_command_req()
        message.command = command

        try:
            await self._send_and_wait_for_completion()
        except CompletionError as e:
            raise ExecuteCommandError(b''.join(self._command_output),
                                      e.error)

        return b''.join(self._command_output)

    async def get_file(self, remote_path, local_path, progress=None):
        if progress is None:
            progress = Progress()

        with open(local_path, 'wb') as self._fget:
            self._get_file_size = None
            self._get_progress = progress
            message = self.init_get_file_req()
            message.path = remote_path

            try:
                await self._send_and_wait_for_completion()
            except CompletionError as e:
                raise GetFileError(remote_path, e.error)

    async def _put_file_open(self, remote_path, size):
        message = self.init_put_file_req()
        message.path = remote_path
        message.size = size
        response = await self._send_and_wait_for_completion()

        return response.window_size

    async def _put_file_data(self, fin, window_size):
        outstanding_requests = 0

        while True:
            while outstanding_requests < window_size:
                message = self.init_put_file_req()
                message.data = fin.read(self._maximum_message_size - 16)

                if message.data:
                    outstanding_requests += 1
                    self.send()
                elif outstanding_requests > 0:
                    break
                else:
                    return

            response = await self._wait_for_completion()
            outstanding_requests -= response.acknowledge_count

    async def _put_file_close(self):
        self.init_put_file_req()
        await self._send_and_wait_for_completion()

    async def put_file(self, fin, size, remote_path):
        try:
            window_size = await self._put_file_open(remote_path, size)
            await self._put_file_data(fin, window_size)
            await self._put_file_close()
        except CompletionError as e:
            raise PutFileError(remote_path, e.error)


def print_info(text):
    print(yellow(f'[bunga {time.strftime("%H:%M:%S")}] {text}', style='bold'))


def print_error(error):
    print(red(f'ERROR({error})', style='bold'))


def format_log_entry(entry):
    header, text = entry.split(']', 1)
    header += ']'

    mo = RE_ML_LOG.match(text)

    if mo:
        date = mo.group(1)
        level = mo.group(2)
        log_object = mo.group(3)
        text = mo.group(4)

        if level in [' EMERGENCY', ' ALERT', ' CRITICAL', ' ERROR']:
            level = red(level, style='bold')
        elif level == ' WARNING':
            level = yellow(level, style='bold')

        text = yellow(date) + level + color(log_object, 'grey') + text
    elif is_error(text):
        text = red(text, style='bold')
    elif is_warning(text):
        test = yellow(text, style='bold')

    return green(header) + text


def print_log_entry(entry, fout):
    print(format_log_entry(entry), flush=True, file=fout)


class ClientThread(threading.Thread):

    def __init__(self, uri, client_class=Client, *args, **kwargs):
        super().__init__()
        LOGGER.info('Server URI: %s', uri)
        self._loop = asyncio.new_event_loop()
        self._client = client_class(uri, self._loop, *args, **kwargs)
        self.daemon = True

    def run(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._start())
        self._loop.run_forever()

    def stop(self):
        pass

    def wait_for_connection(self, timeout=None):
        asyncio.run_coroutine_threadsafe(self._client.wait_for_connection(timeout),
                                         self._loop).result()

    def execute_command(self, command):
        return asyncio.run_coroutine_threadsafe(
            self._client.execute_command(command),
            self._loop).result()

    def get_file(self, remote_path, local_path, progress=None):
        return asyncio.run_coroutine_threadsafe(
            self._client.get_file(remote_path, local_path, progress),
            self._loop).result()

    def put_file(self, fin, size, remote_path):
        return asyncio.run_coroutine_threadsafe(
            self._client.put_file(fin, size, remote_path),
            self._loop).result()

    async def _start(self):
        self._client.start()


def create_to_path(from_path, to_path):
    if to_path:
        return to_path
    else:
        return os.path.basename(from_path)
