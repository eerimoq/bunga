import sys

from ..client import Client
from ..client import ClientThread
from ..client import ExecuteCommandError


def _do_execute(args):
    client = ClientThread(args.uri, Client)
    client.start()
    client.wait_for_connection()

    try:
        sys.stdout.buffer.write(client.execute_command(args.command))
    except ExecuteCommandError as e:
        sys.stdout.buffer.write(e.output)
        sys.stdout.flush()
        sys.exit(e.error)


def add_subparser(subparsers):
    subparser = subparsers.add_parser('execute')
    subparser.add_argument('-u' ,'--uri',
                           default='tcp://127.0.0.1:28000',
                           help='URI of the server (default: %(default)s)')
    subparser.add_argument('command', help='The command to execute.')
    subparser.set_defaults(func=_do_execute)
