import sys
import argparse
import logging

from .version import __version__
from .client import Client
from .client import ClientThread
from .client import ExecuteCommandError


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-l', '--log-level',
                        default='error',
                        choices=[
                            'debug', 'info', 'warning', 'error', 'critical'
                        ],
                        help='Set the logging level (default: %(default)s).')
    parser.add_argument('--version',
                        action='version',
                        version=__version__,
                        help='Print version information and exit.')

    # Workaround to make the subparser required in Python 3.
    subparsers = parser.add_subparsers(title='subcommands',
                                       dest='subcommand')
    subparsers.required = True

    # Import when used for less dependencies. For example, curses is
    # not part of all Python builds.
    from .subparsers import shell
    from .subparsers import get_file
    from .subparsers import put_file
    from .subparsers import log
    from .subparsers import execute

    shell.add_subparser(subparsers)
    get_file.add_subparser(subparsers)
    put_file.add_subparser(subparsers)
    log.add_subparser(subparsers)
    execute.add_subparser(subparsers)

    args = parser.parse_args()

    level = logging.getLevelName(args.log_level.upper())
    logging.basicConfig(level=level, format='%(asctime)s %(message)s')

    if args.debug:
        args.func(args)
    else:
        try:
            args.func(args)
        except BaseException as e:
            sys.exit(f'error: {e}')
