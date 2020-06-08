from tqdm.auto import tqdm

from ..client import ClientThread
from ..client import create_to_path


class ProgressBar:

    def __init__(self):
        self._tqdm = None

    def init(self, total):
        self._tqdm = tqdm(total=total, unit='B', unit_scale=True, unit_divisor=1024)

    def close(self):
        if self._tqdm is not None:
            self._tqdm.close()

    def update(self, size):
        self._tqdm.update(size)


def _do_get_file(args):
    client = ClientThread(args.uri,
                          connection_refused_delay=None,
                          connect_timeout_delay=None)
    client.start()
    client.wait_for_connection()
    localfile = create_to_path(args.remotefile, args.localfile)
    progress = ProgressBar()

    try:
        client.get_file(args.remotefile, localfile, progress=progress)
    finally:
        progress.close()


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
