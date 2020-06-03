import time
import threading
import sys
import logging
import socket
import pexpect
import bunga
import subprocess
import systest
import os


class ServerThread(threading.Thread):

    def __init__(self, listener, handler):
        super().__init__()
        self._listener = listener
        self._handler = handler
        self.daemon = True
        self.exception = None

    def run(self):
        try:
            self._handler(self._listener.accept()[0])
        except Exception as e:
            self.exception = e


def start_server(handler):
    listener = socket.socket()
    listener.bind(('localhost', 0))
    listener.listen()
    server = ServerThread(listener, handler)
    server.start()

    return server, listener.getsockname()[1]


class TestCase(systest.TestCase):

    def __init__(self):
        super().__init__()
        self.server = None
        self.port = None

    def handler(self, client):
        raise NotImplementedError()

    def setup(self):
        self.server, self.port = start_server(self.handler)

    def teardown(self):
        self.server.join()
        self.assert_is_none(self.server.exception)



class ShellTest(TestCase):

    def handler(self, client):
        req = client.recv(10)
        self.assert_equal(req, b'\x01\x00\x00\x06\n\x04\n\x02ls')
        client.sendall(b'\x02\x00\x00\x0f\n\r\n\x0bfoo bar fie')
        client.close()

    def run(self):
        proc = pexpect.spawn(
            f'python3 -m bunga shell --uri tcp://localhost:{self.port}',
            logfile=sys.stdout,
            encoding='utf-8',
            codec_errors='replace')
        proc.expect('\[bunga \d+:\d+:\d+\] Connected')
        proc.sendline('ls')
        proc.expect('foo bar fie')
        proc.sendline('exit')

        while proc.isalive():
            time.sleep(0.1)


class GetFileTest(TestCase):

    def handler(self, client):
        req = client.recv(21)
        self.assert_equal(req, b'\x01\x00\x00\x11\x12\x0f\n\rtests/put.txt')
        client.send(b'\x02\x00\x00\x0f\x1a\r\x08\t\x12\t12345678\n')
        client.send(b'\x02\x00\x00\x02\x1a\x00')
        client.close()

    def run(self):
        if os.path.exists('put.txt'):
            os.remove('put.txt')

        subprocess.check_call(['python3', '-m', 'bunga', 'get_file',
                               '--uri', f'tcp://localhost:{self.port}',
                               'tests/put.txt'])

        with open('put.txt') as fin:
            self.assert_equal(fin.read(), '12345678\n')


class PutFileTest(TestCase):

    def handler(self, client):
        req = client.recv(15)
        self.assert_equal(req, b'\x01\x00\x00\x0b\x1a\t\n\x07put.txt')
        req = client.recv(16)
        self.assert_equal(req, b'\x01\x00\x00\r\x1a\x0b\x12\t12345678')
        client.send(b'\x02\x00\x00\x02"\x00')
        client.close()

    def run(self):
        subprocess.check_call(['python3', '-m', 'bunga', 'put_file',
                               '--uri', f'tcp://localhost:{self.port}',
                               'tests/put.txt'])


class LogTest(TestCase):

    def handler(self, client):
        client.sendall(
            b'\x02\x00\x00\x59\x12W\nU[    0.141826] imx-sdma 20ec000.sdma: '
            b'external firmware not found, using ROM firmware')
        client.sendall(
            b'\x02\x00\x00\x5c\x12Z\nX[    2.497619] 1970-01-01 00:00:02 INFO '
            b'dhcp_client State change from INIT to SELECTING.')
        client.close()

    def run(self):
        proc = pexpect.spawn(
            f'python3 -m bunga log --uri tcp://localhost:{self.port}',
            logfile=sys.stdout,
            encoding='utf-8',
            codec_errors='replace')
        proc.expect('imx')
        proc.close()

        while proc.isalive():
            time.sleep(0.1)


def main():
    sequencer = systest.setup("Bunga", console_log_level=logging.DEBUG)

    sequencer.run(
        ShellTest(),
        GetFileTest(),
        PutFileTest(),
        LogTest()
    )

    sequencer.report_and_exit()


if __name__ == '__main__':
    main()
