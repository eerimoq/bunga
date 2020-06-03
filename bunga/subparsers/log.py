import sys
import time

from ..client import Client
from ..client import ClientThread
from ..client import print_info
from ..client import print_log_entry


class LogClient(Client):

    async def on_connected(self):
        await super().on_connected()
        print_info('Connected')

    async def on_disconnected(self):
        await super().on_disconnected()
        print_info('Disconnected')

    async def on_log_entry_ind(self, message):
        print_log_entry(''.join(message.text), sys.stdout)


def _do_log(args):
    client = ClientThread(args.uri, client_class=LogClient)
    client.start()

    while True:
        time.sleep(100)


def add_subparser(subparsers):
    subparser = subparsers.add_parser('log')
    subparser.add_argument('-u' ,'--uri',
                           default='tcp://127.0.0.1:28000',
                           help='URI of the server (default: %(default)s)')
    subparser.set_defaults(func=_do_log)
