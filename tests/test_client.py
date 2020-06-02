import logging
import asyncio
import unittest

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
        self.connected_event = asyncio.Event()
        self.log_entries = asyncio.Queue()

    async def on_connected(self):
        await super().on_connected()
        self.connected_event.set()

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
            await client.connected_event.wait()

            output, error = await client.execute_command('date')
            self.assertEqual(output, '2020')
            self.assertEqual(error, '')

            output, error = await client.execute_command('bad')
            self.assertEqual(output, '')
            self.assertEqual(error, 'not found')

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
            writer.write(b'\x02\x00\x00\x08\x1a\x06\n\x041234')
            writer.write(b'\x02\x00\x00\x08\x1a\x06\n\x045678')
            writer.write(b'\x02\x00\x00\x02\x1a\x00')

            writer.close()

        listener = await asyncio.start_server(on_client_connected, 'localhost', 0)

        async def client_main():
            client = Client(listener)
            client.start()
            await client.connected_event.wait()

            error = await client.get_file('get_file.txt', '/init')
            self.assertEqual(error, '')

            with open('get_file.txt', 'rb') as fin:
                self.assertEqual(fin.read(), b'12345678')

            client.stop()
            listener.close()

        await asyncio.wait_for(
            asyncio.gather(server_main(listener), client_main()), 2)

    def test_put_file(self):
        asyncio.run(self.put_file())

    async def put_file(self):
        async def on_client_connected(reader, writer):
            req = await reader.readexactly(27)
            self.assertEqual(
                req,
                b'\x01\x00\x00\x17\x1a\x15\n\x13put_file_remote.txt')
            req = await reader.readexactly(17)
            self.assertEqual(req, b'\x01\x00\x00\r\x1a\x0b\x12\t12345678\n')
            req = await reader.readexactly(6)
            self.assertEqual(req, b'\x01\x00\x00\x02\x1a\x00')
            print('asd')
            writer.write(b'\x02\x00\x00\x02"\x00')

            writer.close()

        listener = await asyncio.start_server(on_client_connected, 'localhost', 0)

        async def client_main():
            client = Client(listener)
            client.start()
            await client.connected_event.wait()

            error = await client.put_file('tests/put_file.txt',
                                          'put_file_remote.txt')
            self.assertEqual(error, '')

            client.stop()
            listener.close()

        await asyncio.wait_for(
            asyncio.gather(server_main(listener), client_main()), 2)
