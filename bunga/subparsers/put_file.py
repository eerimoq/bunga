import sys
import os
from tqdm.auto import tqdm
from tqdm.utils import CallbackIOWrapper

from ..client import ClientThread
from ..client import create_to_path


def do_put_file(args):
    if not os.path.exists(args.localfile):
        sys.exit(f"Local file '{args.localfile}' does not exist.")

    client = ClientThread(args.uri,
                          connection_refused_delay=None,
                          connect_timeout_delay=None)
    client.start()
    remotefile = create_to_path(args.localfile, args.remotefile)
    size = os.stat(args.localfile).st_size

    with open(args.localfile, 'rb') as fin:
        with tqdm(total=size,
                  unit='B',
                  unit_scale=True,
                  unit_divisor=1024) as progress:
            client.wait_for_connection()
            client.put_file(CallbackIOWrapper(progress.update, fin, 'read'),
                            size,
                            remotefile)


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
