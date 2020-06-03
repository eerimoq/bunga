from ..client import ClientThread
from ..client import create_to_path


def do_put_file(args):
    client = ClientThread(args.uri)
    client.start()
    remotefile = create_to_path(args.localfile, args.remotefile)
    client.put_file(args.localfile, remotefile)


def add_subparser(subparsers):
    subparser = subparsers.add_parser('put_file')
    subparser.add_argument('-u' ,'--uri',
                           default='tcp://127.0.0.1:28000',
                           help='URI of the server (default: %(default)s)')
    subparser.add_argument('localfile', help='The local file path.')
    subparser.add_argument('remotefile',
                           nargs='?',
                           help='The remote file path.')
    subparser.set_defaults(func=do_put_file)
