import os
import sys
import logging
import asyncio
import unittest
from unittest.mock import patch
from io import StringIO

from colors import red
from colors import green
from colors import yellow
from colors import color

import bunga


def create_tcp_uri(listener):
    address, port = listener.sockets[0].getsockname()

    return f'tcp://{address}:{port}'


async def server_main(listener):
    async with listener:
        try:
            await listener.serve_forever()
        except asyncio.CancelledError:
            pass


class Client(bunga.Client):

    def __init__(self, listener):
        super().__init__(create_tcp_uri(listener), asyncio.get_event_loop())
        self.log_entries = asyncio.Queue()

    async def on_log_entry_ind(self, message):
        await super().on_log_entry_ind(message)
        await self.log_entries.put(''.join(message.text))


class ClientTest(unittest.TestCase):

    async def start_client(self, listener):
        client = Client(listener)
        client.start()
        await client.wait_for_connection()

        return client

    async def connect_req_rsp(self, reader, writer):
        connect_req = await reader.readexactly(6)
        self.assertEqual(connect_req, b'\x01\x00\x00\x02\n\x00')
        writer.write(b'\x02\x00\x00\x07\n\x05\x08\x02\x10\xd8\x01')

    def test_execute_command(self):
        asyncio.run(self.execute_command())

    async def execute_command(self):
        async def on_client_connected(reader, writer):
            await self.connect_req_rsp(reader, writer)
            date_req = await reader.readexactly(12)
            self.assertEqual(date_req, b'\x01\x00\x00\x08\x12\x06\n\x04date')
            writer.write(b'\x02\x00\x00\x08\x12\x06\n\x042020')
            writer.write(b'\x02\x00\x00\x02\x12\x00')

            bad_req = await reader.readexactly(11)
            self.assertEqual(bad_req, b'\x01\x00\x00\x07\x12\x05\n\x03bad')
            writer.write(b'\x02\x00\x00\x0d\x12\x0b\x12\tnot found')

            writer.close()

        listener = await asyncio.start_server(on_client_connected, 'localhost', 0)

        async def client_main():
            client = await self.start_client(listener)

            output = await client.execute_command('date')
            self.assertEqual(output, b'2020')

            with self.assertRaises(bunga.ExecuteCommandError) as cm:
                await client.execute_command('bad')

            self.assertEqual(cm.exception.output, b'')
            self.assertEqual(cm.exception.error, 'not found')

            client.stop()
            listener.close()

        await asyncio.wait_for(
            asyncio.gather(server_main(listener), client_main()), 2)

    def test_execute_command_disconnect_and_no_response(self):
        asyncio.run(self.execute_command_disconnect_and_no_response())

    async def execute_command_disconnect_and_no_response(self):
        async def on_client_connected(reader, writer):
            await self.connect_req_rsp(reader, writer)
            date_req = await reader.readexactly(12)
            self.assertEqual(date_req, b'\x01\x00\x00\x08\x12\x06\n\x04date')
            writer.close()

        listener = await asyncio.start_server(on_client_connected, 'localhost', 0)

        async def client_main():
            client = await self.start_client(listener)

            with self.assertRaises(bunga.ExecuteCommandError) as cm:
                await client.execute_command('date')

            self.assertEqual(cm.exception.output, b'')
            self.assertEqual(cm.exception.error, 'Connection lost.')

            client.stop()
            listener.close()

        await asyncio.wait_for(
            asyncio.gather(server_main(listener), client_main()), 2)

    def test_log_entry(self):
        asyncio.run(self.log_entry())

    async def log_entry(self):
        async def on_client_connected(reader, writer):
            await self.connect_req_rsp(reader, writer)
            writer.write(b'\x02\x00\x00\x0f\x1a\r\n\x03123\n\x06Hello!')
            writer.write(b'\x02\x00\x00\x15\x1a\x13\n\x03123\n\x06Hello!\n\x04 Hi!')
            writer.close()

        listener = await asyncio.start_server(on_client_connected, 'localhost', 0)

        async def client_main():
            client = await self.start_client(listener)
            log_entry = await client.log_entries.get()
            self.assertEqual(log_entry, '123Hello!')
            log_entry = await client.log_entries.get()
            self.assertEqual(log_entry, '123Hello! Hi!')
            client.stop()
            listener.close()

        await asyncio.wait_for(
            asyncio.gather(server_main(listener), client_main()), 2)

    def test_get_file(self):
        asyncio.run(self.get_file())

    async def get_file(self):
        async def on_client_connected(reader, writer):
            await self.connect_req_rsp(reader, writer)

            # Open.
            req = await reader.readexactly(13)
            self.assertEqual(req, b'\x01\x00\x00\x09\x1a\x07\n\x05/init')
            writer.write(b'\x02\x00\x00\x0a"\x08\x08\x08\x12\x041234')

            # Data.
            req = await reader.readexactly(8)
            self.assertEqual(req, b'\x01\x00\x00\x04\x1a\x02\x18\x01')
            writer.write(b'\x02\x00\x00\x08"\x06\x12\x045678')

            # Close.
            req = await reader.readexactly(8)
            self.assertEqual(req, b'\x01\x00\x00\x04\x1a\x02\x18\x01')
            writer.write(b'\x02\x00\x00\x02"\x00')

            writer.close()

        listener = await asyncio.start_server(on_client_connected, 'localhost', 0)

        async def client_main():
            client = await self.start_client(listener)

            await client.get_file('/init', 'get.txt')

            with open('get.txt', 'rb') as fin:
                self.assertEqual(fin.read(), b'12345678')

            client.stop()
            listener.close()

        await asyncio.wait_for(
            asyncio.gather(server_main(listener), client_main()), 2)

    def test_put_file(self):
        asyncio.run(self.put_file())

    async def put_file(self):
        async def on_client_connected(reader, writer):
            await self.connect_req_rsp(reader, writer)

            # Setup.
            req = await reader.readexactly(25)
            self.assertEqual(len(req), 25)
            self.assertEqual(
                req,
                b'\x01\x00\x00\x15"\x13\n\x0eput_remote.txt\x10\x89\x04')
            writer.write(b'\x02\x00\x00\x06*\x04\x08\n\x18\x01')

            # Data.
            req = await reader.readexactly(210)
            self.assertEqual(len(req), 210)
            self.assertEqual(
                req,
                b'\x01\x00\x00\xce"\xcb\x01\x1a\xc8\x0112345678901234567890123456'
                b'789012345678901234567890123456789012345678901234567890123456789012'
                b'345678901234567890123456789012345678901234567890123456789012345678'
                b'901234567890123456789012345678901234567890')

            req = await reader.readexactly(210)
            self.assertEqual(len(req), 210)
            self.assertEqual(
                req,
                b'\x01\x00\x00\xce"\xcb\x01\x1a\xc8\x0112345678901234567890123456'
                b'789012345678901234567890123456789012345678901234567890123456789012'
                b'345678901234567890123456789012345678901234567890123456789012345678'
                b'901234567890123456789012345678901234567890')

            req = await reader.readexactly(129)
            self.assertEqual(len(req), 129)
            self.assertEqual(
                req,
                b'\x01\x00\x00}"{\x1ay1234567890123456789012345678901234567890123'
                b'456789012345678901234567890123456789012345678901234567890123456789'
                b'01234567890\n')

            writer.write(b'\x02\x00\x00\x04*\x02\x18\x01')
            writer.write(b'\x02\x00\x00\x04*\x02\x18\x01')
            writer.write(b'\x02\x00\x00\x04*\x02\x18\x01')

            # Finalize.
            req = await reader.readexactly(6)
            self.assertEqual(req, b'\x01\x00\x00\x02"\x00')
            writer.write(b'\x02\x00\x00\x04*\x02\x18\x01')
            writer.close()

        listener = await asyncio.start_server(on_client_connected, 'localhost', 0)

        async def client_main():
            client = await self.start_client(listener)

            with open('tests/put.txt', 'rb') as fin:
                await client.put_file(fin,
                                      os.stat('tests/put.txt').st_size,
                                      'put_remote.txt')

            client.stop()
            listener.close()

        await asyncio.wait_for(
            asyncio.gather(server_main(listener), client_main()), 2)

    def test_print_log_entry(self):
        stdout = StringIO()

        with patch('sys.stdout', stdout):
            bunga.client.print_log_entry(
                '[    0.141804] imx-sdma 20ec000.sdma: Direct firmware load for '
                'imx/sdma/sdma-imx6q.bin failed with error -2',
                sys.stdout)
            bunga.client.print_log_entry(
                '[    0.141826] imx-sdma 20ec000.sdma: external firmware not '
                'found, using ROM firmware',
                sys.stdout)
            bunga.client.print_log_entry(
                '[    2.497619] 1970-01-01 00:00:02 INFO dhcp_client State change '
                'from INIT to SELECTING.',
                sys.stdout)

        self.assertEqual(
            stdout.getvalue(),
            green('[    0.141804]')
            + red(' imx-sdma 20ec000.sdma: Direct firmware load for '
                  'imx/sdma/sdma-imx6q.bin failed with error -2', style='bold')
            + '\n'
            + green('[    0.141826]')
            + (' imx-sdma 20ec000.sdma: external firmware not found, using ROM '
               'firmware\n')
            + green('[    2.497619]')
            + yellow(' 1970-01-01 00:00:02')
            + ' INFO'
            + color(' dhcp_client', 'grey')
            + ' State change from INIT to SELECTING.\n')
