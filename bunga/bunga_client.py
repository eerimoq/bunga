# This file was generated by Messi.

import asyncio
import logging
import bitstruct

from . import bunga_pb2


LOGGER = logging.getLogger(__name__)

CF_HEADER = bitstruct.compile('u8u24')


class MessageType:

    CLIENT_TO_SERVER_USER = 1
    SERVER_TO_CLIENT_USER = 2
    PING = 3
    PONG = 4


def parse_tcp_uri(uri):
    """Parse tcp://<host>:<port>.

    """

    try:
        if uri[:6] != 'tcp://':
            raise ValueError

        address, port = uri[6:].split(':')

        return address, int(port)
    except (ValueError, TypeError):
        raise ValueError(
            f"Expected URI on the form tcp://<host>:<port>, but got '{uri}'.")


class BungaClient:

    def __init__(self, uri, keep_alive_interval=2, connect_timeout=5):
        self._address, self._port = parse_tcp_uri(uri)
        self._uri = uri
        self._keep_alive_interval = keep_alive_interval
        self._connect_timeout = connect_timeout
        self._reader = None
        self._writer = None
        self._task = None
        self._keep_alive_task = None
        self._pong_event = None
        self._output = None

    def start(self):
        """Connect to the server. `on_connected()` is called once
        connected. Automatic reconnect if disconnected.

        """

        if self._task is None:
            self._task = asyncio.create_task(self._main())

    def stop(self):
        """Disconnect from the server (if connected). Call `start()` to
        connect again.

        """

        if self._task is not None:
            self._task.cancel()
            self._task = None

    def send(self):
        """Send prepared message to the server.

        """

        encoded = self._output.SerializeToString()
        header = CF_HEADER.pack(MessageType.CLIENT_TO_SERVER_USER, len(encoded))
        self._writer.write(header + encoded)

    async def on_connected(self):
        """Called when connected to the server.

        """

    async def on_disconnected(self):
        """Called when disconnected from the server.

        """

    async def on_connect_failure(self, exception):
        """Called when a connection attempt to the server fails. Returns the
        number of seconds to wait before trying to connect again, or
        ``None`` never to connect again.

        """

        if isinstance(exception, ConnectionRefusedError):
            return 1
        else:
            return 0

    async def on_connect_rsp(self, message):
        """Called when a connect_rsp message is received from the server.

        """

    async def on_execute_command_rsp(self, message):
        """Called when a execute_command_rsp message is received from the server.

        """

    async def on_log_entry_ind(self, message):
        """Called when a log_entry_ind message is received from the server.

        """

    async def on_get_file_rsp(self, message):
        """Called when a get_file_rsp message is received from the server.

        """

    async def on_put_file_rsp(self, message):
        """Called when a put_file_rsp message is received from the server.

        """

    def init_connect_req(self):
        """Prepare a connect_req message. Call `send()` to send it.

        """

        self._output = bunga_pb2.ClientToServer()
        self._output.connect_req.SetInParent()

        return self._output.connect_req

    def init_execute_command_req(self):
        """Prepare a execute_command_req message. Call `send()` to send it.

        """

        self._output = bunga_pb2.ClientToServer()
        self._output.execute_command_req.SetInParent()

        return self._output.execute_command_req

    def init_get_file_req(self):
        """Prepare a get_file_req message. Call `send()` to send it.

        """

        self._output = bunga_pb2.ClientToServer()
        self._output.get_file_req.SetInParent()

        return self._output.get_file_req

    def init_put_file_req(self):
        """Prepare a put_file_req message. Call `send()` to send it.

        """

        self._output = bunga_pb2.ClientToServer()
        self._output.put_file_req.SetInParent()

        return self._output.put_file_req

    async def _main(self):
        while True:
            if not await self._connect():
                break

            await self.on_connected()
            self._pong_event = asyncio.Event()
            self._keep_alive_task = asyncio.create_task(self._keep_alive_main())

            try:
                await self._reader_loop()
            except (Exception, asyncio.CancelledError) as e:
                LOGGER.info('Reader loop stopped by %r.', e)
                self._close()

            self._keep_alive_task.cancel()
            await self.on_disconnected()

    async def _connect(self):
        """Repeatedly try to connect to the server. Returns ``True`` if a
        connection has been established, and ``False`` otherwise.

        """

        while True:
            try:
                self._reader, self._writer = await asyncio.wait_for(
                    asyncio.open_connection(self._address, self._port),
                    self._connect_timeout)

                return True
            except ConnectionRefusedError as e:
                LOGGER.info("Connection refused.")
                delay = await self.on_connect_failure(e)
            except asyncio.TimeoutError as e:
                LOGGER.info("Connect timeout.")
                delay = await self.on_connect_failure(e)

            if delay is None:
                return False

            await asyncio.sleep(delay)

    async def _handle_user_message(self, payload):
        message = bunga_pb2.ServerToClient()
        message.ParseFromString(payload)
        choice = message.WhichOneof('messages')

        if choice == 'connect_rsp':
            await self.on_connect_rsp(message.connect_rsp)
        elif choice == 'execute_command_rsp':
            await self.on_execute_command_rsp(message.execute_command_rsp)
        elif choice == 'log_entry_ind':
            await self.on_log_entry_ind(message.log_entry_ind)
        elif choice == 'get_file_rsp':
            await self.on_get_file_rsp(message.get_file_rsp)
        elif choice == 'put_file_rsp':
            await self.on_put_file_rsp(message.put_file_rsp)

    def _handle_pong(self):
        self._pong_event.set()

    async def _reader_loop(self):
        while True:
            header = await self._reader.readexactly(4)
            message_type, size = CF_HEADER.unpack(header)
            payload = await self._reader.readexactly(size)

            if message_type == MessageType.SERVER_TO_CLIENT_USER:
                await self._handle_user_message(payload)
            elif message_type == MessageType.PONG:
                self._handle_pong()

    async def _keep_alive_loop(self):
        while True:
            await asyncio.sleep(self._keep_alive_interval)
            self._pong_event.clear()
            self._writer.write(CF_HEADER.pack(MessageType.PING, 0))
            await asyncio.wait_for(self._pong_event.wait(),
                                   self._keep_alive_interval)

    async def _keep_alive_main(self):
        try:
            await self._keep_alive_loop()
        except (Exception, asyncio.CancelledError) as e:
            LOGGER.info('Keep alive task stopped by %r.', e)
            self._close()

    def _close(self):
        if self._writer is not None:
            self._writer.close()
            self._writer = None
