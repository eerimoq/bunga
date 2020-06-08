from ..client import Client
from ..client import ClientThread


def _do_execute(args):
    client = ClientThread(args.uri, Client)
    client.start()
    client.wait_for_connection()

    for command in args.commands:
        client.execute_command(command)


def add_subparser(subparsers):
    subparser = subparsers.add_parser('execute')
    subparser.add_argument('-u' ,'--uri',
                           default='tcp://127.0.0.1:28000',
                           help='URI of the server (default: %(default)s)')
    subparser.add_argument('commands',
                           nargs='+',
                           help='One or more commands to execute.')
    subparser.set_defaults(func=_do_execute)
