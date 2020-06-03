import time

from ..client import ClientThread


def _do_log(args):
    client = ClientThread(args.uri, print_log_entries=True)
    client.start()

    while True:
        time.sleep(100)


def add_subparser(subparsers):
    subparser = subparsers.add_parser('log')
    subparser.add_argument('-u' ,'--uri',
                           default='tcp://127.0.0.1:28000',
                           help='URI of the server (default: %(default)s)')
    subparser.set_defaults(func=_do_log)
