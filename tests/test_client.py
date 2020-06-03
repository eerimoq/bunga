import sys
import logging
import asyncio
import unittest
from unittest.mock import patch
from io import StringIO

from colors import red
from colors import green
from colors import yellow

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

    def test_execute_command(self):
        asyncio.run(self.execute_command())

    async def execute_command(self):
        async def on_client_connected(reader, writer):
            date_req = await reader.readexactly(12)
            self.assertEqual(date_req, b'\x01\x00\x00\x08\n\x06\n\x04date')
            writer.write(b'\x02\x00\x00\x08\x0a\x06\x0a\x04\x32\x30\x32\x30')
            writer.write(b'\x02\x00\x00\x02\x0a\x00')

            bad_req = await reader.readexactly(11)
            self.assertEqual(bad_req, b'\x01\x00\x00\x07\n\x05\n\x03bad')
            writer.write(b'\x02\x00\x00\x0d\x0a\x0b\x12\x09\x6e\x6f\x74\x20\x66'
                         b'\x6f\x75\x6e\x64')

            writer.close()

        listener = await asyncio.start_server(on_client_connected, 'localhost', 0)

        async def client_main():
            client = Client(listener)
            client.start()

            output = await client.execute_command('date')
            self.assertEqual(output, '2020')

            with self.assertRaises(bunga.ExecuteCommandError) as cm:
                await client.execute_command('bad')

            self.assertEqual(cm.exception.output, '')
            self.assertEqual(cm.exception.error, 'not found')

            client.stop()
            listener.close()

        await asyncio.wait_for(
            asyncio.gather(server_main(listener), client_main()), 2)

    def test_log_entry(self):
        asyncio.run(self.log_entry())

    async def log_entry(self):
        async def on_client_connected(reader, writer):
            writer.write(b'\x02\x00\x00\x0f\x12\r\n\x03123\n\x06Hello!')
            writer.write(b'\x02\x00\x00\x15\x12\x13\n\x03123\n\x06Hello!\n\x04 Hi!')
            writer.close()

        listener = await asyncio.start_server(on_client_connected, 'localhost', 0)

        async def client_main():
            client = Client(listener)
            client.start()
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
            req = await reader.readexactly(13)
            self.assertEqual(req, b'\x01\x00\x00\x09\x12\x07\n\x05/init')
            writer.write(b'\x02\x00\x00\x0a\x1a\x08\x08\x08\x12\x041234')
            writer.write(b'\x02\x00\x00\x08\x1a\x06\x12\x045678')
            writer.write(b'\x02\x00\x00\x02\x1a\x00')

            writer.close()

        listener = await asyncio.start_server(on_client_connected, 'localhost', 0)

        async def client_main():
            client = Client(listener)
            client.start()

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
            req = await reader.readexactly(22)
            self.assertEqual(
                req,
                b'\x01\x00\x00\x12\x1a\x10\n\x0eput_remote.txt')
            req = await reader.readexactly(17)
            self.assertEqual(req, b'\x01\x00\x00\r\x1a\x0b\x12\t12345678\n')
            req = await reader.readexactly(6)
            self.assertEqual(req, b'\x01\x00\x00\x02\x1a\x00')
            writer.write(b'\x02\x00\x00\x02"\x00')

            writer.close()

        listener = await asyncio.start_server(on_client_connected, 'localhost', 0)

        async def client_main():
            client = Client(listener)
            client.start()

            await client.put_file('tests/put.txt', 'put_remote.txt')

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
            + yellow(' 1970-01-01 00:00:02 ')
            + ('INFO dhcp_client State change from INIT to SELECTING.\n'))
