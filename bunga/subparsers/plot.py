import os
import threading
import re
import time
import curses
from datetime import datetime
import queue
import math
import json
import fractions
from collections import deque
import irwin.timeseries

from ..client import ClientThread
from ..client import NotConnectedError
from ..client import ExecuteCommandError


DEFAULT_CONFIG = {
    'eth0-tx': {
        'title': 'eth0 tx [bytes/s]',
        'command': 'cat proc/net/dev',
        'pattern': '^\s*eth0:' + 8 * '\s+\d+' + '\s+(\d+)',
        'algorithm': 'delta'
    },
    'eth0-rx': {
        'title': 'eth0 rx [bytes/s]',
        'command': 'cat proc/net/dev',
        'pattern': '^\s*eth0:\s+(\d+)',
        'algorithm': 'delta'
    },
    'uptime': {
        'title': 'Uptime [s]',
        'command': 'cat proc/uptime'
    },
    'cpu': {
        'title': 'CPU [%]',
        'command': 'cat proc/stat',
        'pattern': 'cpu' + 3 * '\s+\d+' + '\s+(\d+)',
        'algorithm': 'delta',
        'scale': -1,
        'offset': 100,
        'y-min': 0,
        'y-max': 100
    }
}


class Producer(irwin.timeseries.Producer):

    def __init__(self, uri, config):
        super().__init__(config['interval'])
        self._command = config['command']
        self._re_value = re.compile(config['pattern'], re.MULTILINE)
        self._client = ClientThread(uri)
        self._client.start()

    def execute_command(self):
            try:
                output = self._client.execute_command(self._command).decode()
                mo = self._re_value.search(output)

                if mo:
                    output = mo.group(1)
                else:
                    output = None
            except NotConnectedError:
                output = None
            except ExecuteCommandError:
                output = None

            return output

    def is_connected(self):
        return self._client.is_connected()


def load_config(path, name):
    if os.path.isfile(path):
        with open(path, 'r') as fin:
            config = json.load(fin)
    else:
        print(f"Plot configuration file '{path}' does not exist. Using default "
              f"configuration.")
        config = DEFAULT_CONFIG
        path = 'built-in.json'

    try:
        config = config[name]
    except KeyError:
        message = f"Plot '{name}' is not defined in configuration file '{path}'.\n"
        message += '\n'
        message += 'Defined plots are:\n'
        message += '\n'

        for name in config:
            message += f'  {name}\n'

        raise Exception(message)

    if 'title' not in config:
        config['title'] = 'Untitled'

    if 'command' not in config:
        raise Exception('No command found.')

    if 'pattern' not in config:
        config['pattern'] = '([\d\.]+)'

    if 'algorithm' not in config:
        config['algorithm'] = 'normal'

    if 'interval' not in config:
        config['interval'] = 1

    if 'timespan' not in config:
        config['timespan'] = 60

    if 'scale' not in config:
        config['scale'] = 1

    if 'offset' not in config:
        config['offset'] = 0

    if 'y-min' not in config:
        config['y-min'] = None

    if 'y-max' not in config:
        config['y-max'] = None

    if 'y-lower-limit' not in config:
        config['y-lower-limit'] = config['y-min']

    if 'y-upper-limit' not in config:
        config['y-upper-limit'] = config['y-max']

    if config['interval'] < 1:
        raise Exception('Interval must be at least one.')

    if config['timespan'] < 1:
        raise Exception('Timespan must be at least one.')

    if config['interval'] >= config['timespan']:
        raise Exception(f'Interval must be smaller than timespan.')

    if 'max-age' not in config:
        config['max-age'] = 16 * config['timespan']

    return config


def _do_plot(args):
    config = load_config(os.path.expanduser('~/.bunga-plot.json'),
                         args.name)
    irwin.timeseries.run_curses(config['title'],
                                [],
                                [],
                                Producer(args.uri, config),
                                config['algorithm'],
                                config['y-min'],
                                config['y-max'],
                                config['y-lower-limit'],
                                config['y-upper-limit'],
                                config['scale'],
                                config['offset'],
                                config['max-age'],
                                config['interval'],
                                config['timespan'])


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'plot',
        description='Plot any command output over time.')
    subparser.add_argument('-u' ,'--uri',
                           default='tcp://127.0.0.1:28000',
                           help='URI of the server (default: %(default)s)')
    subparser.add_argument('name', help='Plot name.')
    subparser.set_defaults(func=_do_plot)
