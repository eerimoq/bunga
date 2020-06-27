import threading
import sys
import socket
import bunga
import bunga.subparsers.shell
import os
import unittest
from unittest.mock import patch
from io import StringIO

from .utils import start_server


class CommandLineTest(unittest.TestCase):

    def connect_req_rsp(self, client):
        connect_req = client.recv(6)
        self.assertEqual(connect_req, b'\x01\x00\x00\x02\n\x00')
        client.sendall(b'\x02\x00\x00\x07\n\x05\x08\x02\x10\xd8\x01')

    def shell_handler(self, client):
        self.connect_req_rsp(client)
        req = client.recv(10)
        self.assertEqual(req, b'\x01\x00\x00\x06\x12\x04\n\x02ko')
        client.sendall(b'\x02\x00\x00\x0d\x12\x0b\x12\tNot found')
        req = client.recv(10)
        self.assertEqual(req, b'\x01\x00\x00\x06\x12\x04\n\x02ls')
        client.sendall(b'\x02\x00\x00\x0f\x12\r\n\x0bfoo bar fie')
        client.sendall(b'\x02\x00\x00\x02\x12\x00')
        client.close()

    def test_shell(self):
        server, port = start_server(self.shell_handler)
        stdout = StringIO()

        with patch('sys.stdout', stdout):
            client = bunga.ClientThread(f'tcp://localhost:{port}',
                                        bunga.subparsers.shell.ShellClient)
            client.start()
            client.wait_for_connection()

            with self.assertRaises(bunga.ExecuteCommandError) as cm:
                client.execute_command('ko')

            self.assertEqual(str(cm.exception.error), 'Not found')

            output = client.execute_command('ls')
            self.assertIn(b'foo bar fie', output)
            client.stop()

        server.join()
        self.assertIsNone(server.exception)

    def get_file_handler(self, client):
        self.connect_req_rsp(client)

        # Open.
        req = client.recv(21)
        self.assertEqual(req, b'\x01\x00\x00\x11\x1a\x0f\n\rtests/put.txt')
        client.sendall(b'\x02\x00\x00\x0f"\r\x08\t\x12\t12345678\n')

        # Close.
        req = client.recv(8)
        self.assertEqual(req, b'\x01\x00\x00\x04\x1a\x02\x18\x01')
        client.sendall(b'\x02\x00\x00\x02"\x00')

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
        self.connect_req_rsp(client)
        req = client.recv(21)
        self.assertEqual(req, b'\x01\x00\x00\x11\x1a\x0f\n\rtests/put.txt')
        client.sendall(b'\x02\x00\x00\x0d"\x0b\x1a\tNot found')
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

            self.assertEqual(str(cm.exception),
                             "Failed to get 'tests/put.txt' with error 'Not found'.")

        server.join()
        self.assertIsNone(server.exception)

    def put_file_handler(self, client):
        self.connect_req_rsp(client)

        # Setup.
        req = client.recv(18)
        self.assertEqual(len(req), 18)
        self.assertEqual(req, b'\x01\x00\x00\x0e"\x0c\n\x07put.txt\x10\x89\x04')
        client.sendall(b'\x02\x00\x00\x06*\x04\x08\n\x18\x01')

        # Data.
        req = client.recv(210)
        self.assertEqual(len(req), 210)
        self.assertEqual(
            req,
            b'\x01\x00\x00\xce"\xcb\x01\x1a\xc8\x0112345678901234567890123456'
            b'789012345678901234567890123456789012345678901234567890123456789012'
            b'345678901234567890123456789012345678901234567890123456789012345678'
            b'901234567890123456789012345678901234567890')

        req = client.recv(210)
        self.assertEqual(len(req), 210)
        self.assertEqual(
            req,
            b'\x01\x00\x00\xce"\xcb\x01\x1a\xc8\x0112345678901234567890123456'
            b'789012345678901234567890123456789012345678901234567890123456789012'
            b'345678901234567890123456789012345678901234567890123456789012345678'
            b'901234567890123456789012345678901234567890')

        req = client.recv(129)
        self.assertEqual(len(req), 129)
        self.assertEqual(
            req,
            b'\x01\x00\x00}"{\x1ay1234567890123456789012345678901234567890123'
            b'456789012345678901234567890123456789012345678901234567890123456789'
            b'01234567890\n')

        client.sendall(b'\x02\x00\x00\x04*\x02\x18\x01')
        client.sendall(b'\x02\x00\x00\x04*\x02\x18\x01')
        client.sendall(b'\x02\x00\x00\x04*\x02\x18\x01')

        # Finalize.
        req = client.recv(6)
        self.assertEqual(req, b'\x01\x00\x00\x02"\x00')
        client.sendall(b'\x02\x00\x00\x04*\x02\x18\x01')
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
        self.connect_req_rsp(client)

        # Setup.
        req = client.recv(18)
        self.assertEqual(len(req), 18)
        self.assertEqual(req, b'\x01\x00\x00\x0e"\x0c\n\x07put.txt\x10\x89\x04')
        client.sendall(b'\x02\x00\x00\x07*\x05\x12\x03bad')
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

            self.assertEqual(str(cm.exception),
                             "Failed to put 'put.txt' with error 'bad'.")

        server.join()
        self.assertIsNone(server.exception)
