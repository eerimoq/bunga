from ..client import ClientThread


def _do_monitor(args):
    client = ClientThread(args.uri, print_log_entries=True)
    client.start()


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'monitor',
        description='Monitor yout system in a text based user interface.')
    subparser.add_argument('-u' ,'--uri',
                           default='tcp://127.0.0.1:28000',
                           help='URI of the server (default: %(default)s)')
    subparser.set_defaults(func=_do_monitor)
