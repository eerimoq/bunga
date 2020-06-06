from ..client import ClientThread
from ..client import create_to_path


def _do_get_file(args):
    client = ClientThread(args.uri,
                          connection_refused_delay=None,
                          connect_timeout_delay=None)
    client.start()
    localfile = create_to_path(args.remotefile, args.localfile)
    client.get_file(args.remotefile, localfile)


def add_subparser(subparsers):
    subparser = subparsers.add_parser('get_file')
    subparser.add_argument('-u' ,'--uri',
                           default='tcp://127.0.0.1:28000',
                           help='URI of the server (default: %(default)s)')
    subparser.add_argument('remotefile', help='The remote file path.')
    subparser.add_argument('localfile',
                           nargs='?',
                           help='The local file path.')
    subparser.set_defaults(func=_do_get_file)
