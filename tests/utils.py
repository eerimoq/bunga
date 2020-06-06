import threading
import socket


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
