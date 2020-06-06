import threading
import sys
import socket
import bunga
import bunga.subparsers.shell
import os
import unittest
from unittest.mock import patch
from io import StringIO


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
            raise

        self._listener.close()


def start_server(handler):
    listener = socket.socket()
    listener.bind(('localhost', 0))
    listener.listen()
    server = ServerThread(listener, handler)
    server.start()

    return server, listener.getsockname()[1]


class CommandLineTest(unittest.TestCase):

    def shell_handler(self, client):
        req = client.recv(10)
        self.assertEqual(req, b'\x01\x00\x00\x06\n\x04\n\x02ko')
        client.sendall(b'\x02\x00\x00\x0d\n\x0b\x12\tNot found')
        req = client.recv(10)
        self.assertEqual(req, b'\x01\x00\x00\x06\n\x04\n\x02ls')
        client.sendall(b'\x02\x00\x00\x0f\n\r\n\x0bfoo bar fie')
        client.sendall(b'\x02\x00\x00\x02\n\x00')
        client.close()

    def test_shell(self):
        server, port = start_server(self.shell_handler)
        stdout = StringIO()

        with patch('sys.stdout', stdout):
            client = bunga.ClientThread(f'tcp://localhost:{port}',
                                        bunga.subparsers.shell.ShellClient)
            client.start()

            with self.assertRaises(bunga.ExecuteCommandError) as cm:
                client.execute_command('ko')

            self.assertEqual(str(cm.exception.error), 'Not found')

            output = client.execute_command('ls')
            self.assertIn(b'foo bar fie', output)
            client.stop()

        server.join()
        self.assertIsNone(server.exception)

    def get_file_handler(self, client):
        req = client.recv(21)
        self.assertEqual(req, b'\x01\x00\x00\x11\x12\x0f\n\rtests/put.txt')
        client.sendall(b'\x02\x00\x00\x0f\x1a\r\x08\t\x12\t12345678\n')
        client.sendall(b'\x02\x00\x00\x02\x1a\x00')
        client.close()

    def test_get_file(self):
        server, port = start_server(self.get_file_handler)
        argv = [
            'bunga', 'get_file',
            '--uri', f'tcp://localhost:{port}',
            'tests/put.txt'
        ]

        if os.path.exists('put.txt'):
            os.remove('put.txt')

        with patch('sys.argv', argv):
            bunga.main()

        with open('put.txt') as fin:
            self.assertEqual(fin.read(), '12345678\n')

        server.join()
        self.assertIsNone(server.exception)

    def get_file_error_handler(self, client):
        req = client.recv(21)
        self.assertEqual(req, b'\x01\x00\x00\x11\x12\x0f\n\rtests/put.txt')
        client.sendall(b'\x02\x00\x00\x0d\x1a\x0b\x1a\tNot found')
        client.close()

    def test_get_file_error(self):
        server, port = start_server(self.get_file_error_handler)
        argv = [
            'bunga', '-d', 'get_file',
            '--uri', f'tcp://localhost:{port}',
            'tests/put.txt'
        ]

        with patch('sys.argv', argv):
            with self.assertRaises(Exception) as cm:
                bunga.main()

            self.assertEqual(str(cm.exception), 'Not found')

        server.join()
        self.assertIsNone(server.exception)

    def put_file_handler(self, client):
        # Setup.
        req = client.recv(18)
        self.assertEqual(len(req), 18)
        self.assertEqual(req, b'\x01\x00\x00\x0e\x1a\x0c\n\x07put.txt\x10\x89\x04')
        client.sendall(b'\x02\x00\x00\x04"\x02\x08\n')

        # Data.
        req = client.recv(210)
        self.assertEqual(len(req), 210)
        self.assertEqual(
            req,
            b'\x01\x00\x00\xce\x1a\xcb\x01\x1a\xc8\x0112345678901234567890123456'
            b'789012345678901234567890123456789012345678901234567890123456789012'
            b'345678901234567890123456789012345678901234567890123456789012345678'
            b'901234567890123456789012345678901234567890')

        req = client.recv(210)
        self.assertEqual(len(req), 210)
        self.assertEqual(
            req,
            b'\x01\x00\x00\xce\x1a\xcb\x01\x1a\xc8\x0112345678901234567890123456'
            b'789012345678901234567890123456789012345678901234567890123456789012'
            b'345678901234567890123456789012345678901234567890123456789012345678'
            b'901234567890123456789012345678901234567890')

        req = client.recv(129)
        self.assertEqual(len(req), 129)
        self.assertEqual(
            req,
            b'\x01\x00\x00}\x1a{\x1ay1234567890123456789012345678901234567890123'
            b'456789012345678901234567890123456789012345678901234567890123456789'
            b'01234567890\n')

        client.sendall(b'\x02\x00\x00\x02"\x00')
        client.sendall(b'\x02\x00\x00\x02"\x00')
        client.sendall(b'\x02\x00\x00\x02"\x00')

        # Finalize.
        req = client.recv(6)
        self.assertEqual(req, b'\x01\x00\x00\x02\x1a\x00')
        client.sendall(b'\x02\x00\x00\x02"\x00')
        client.close()

    def test_put_file(self):
        server, port = start_server(self.put_file_handler)
        argv = [
            'bunga', 'put_file',
            '--uri', f'tcp://localhost:{port}',
            'tests/put.txt'
        ]

        with patch('sys.argv', argv):
            bunga.main()

        server.join()
        self.assertIsNone(server.exception)

    def put_file_error_handler(self, client):
        # Setup.
        req = client.recv(18)
        self.assertEqual(len(req), 18)
        self.assertEqual(req, b'\x01\x00\x00\x0e\x1a\x0c\n\x07put.txt\x10\x89\x04')
        client.sendall(b'\x02\x00\x00\x07"\x05\x12\x03bad')
        client.close()

    def test_put_file_error(self):
        server, port = start_server(self.put_file_error_handler)
        argv = [
            'bunga', '-d', 'put_file',
            '--uri', f'tcp://localhost:{port}',
            'tests/put.txt'
        ]

        with patch('sys.argv', argv):
            with self.assertRaises(Exception) as cm:
                bunga.main()

            self.assertEqual(str(cm.exception), 'bad')

        server.join()
        self.assertIsNone(server.exception)
