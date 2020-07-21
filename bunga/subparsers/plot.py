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
import irwin

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

HELP_TEXT = '''\
Quit: q or <Ctrl-C>
Move: <Left>, <Right>, <Up> and <Down>
Zoom: <Ctrl-Up> and <Ctrl-Down>
Pause: <Space>
Reset: r
Clear: c
Help: h or ?\
'''

HELP_NCOLS = 60

RE_SPLIT = re.compile(r'⠀*([^⠀]+)')


def format_clock(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')


class Producer(threading.Thread):

    def __init__(self, uri, config, output_queue):
        super().__init__()
        self._output_queue = output_queue
        self.daemon = True
        self._command = config['command']
        self._interval = config['interval']
        self._client = ClientThread(uri)

    def run(self):
        self._client.start()

        while True:
            timestamp = time.time()

            try:
                output = self._client.execute_command(self._command)
            except NotConnectedError:
                output = None
            except ExecuteCommandError:
                output = None

            self._output_queue.put((timestamp, output))
            time.sleep(self._interval)

    def is_connected(self):
        return self._client.is_connected()


class QuitError(Exception):
    pass


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


def is_y_axis_grid_row(frame_nrows, row):
    return ((frame_nrows - row - 4) % 6) == 0


def zoom_number_to_text(zoom):
    return str(fractions.Fraction(zoom))


class Plot:

    def __init__(self, stdscr, config, args):
        self._config = config
        self._stdscr = stdscr
        self._output_queue = queue.Queue()
        self._nrows, self._ncols = stdscr.getmaxyx()
        self._modified = True
        self._show_help = False
        self._playing = True
        self._data = deque(maxlen=int(config['max-age'] / config['interval']))
        self._timespan = config['timespan']
        self._re_value = re.compile(config['pattern'], re.MULTILINE)
        self._valuespan = 1
        self._x_axis_center = None
        self._y_axis_center = None
        self._x_axis_zoom = 1
        self._y_axis_zoom = 1
        self._x_axis_maximum = time.time()
        self._y_axis_maximum = 0
        self._algorithm = config['algorithm']
        self._scale = config['scale']
        self._offset = config['offset']
        self._y_min = config['y-min']
        self._y_max = config['y-max']
        self._previous_timestamp = None
        self._previous_value = None
        self._y_lower_limit = config['y-lower-limit']
        self._y_upper_limit = config['y-upper-limit']

        stdscr.keypad(True)
        stdscr.nodelay(True)
        curses.use_default_colors()
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_RED, -1)

        self._producer = Producer(args.uri, config, self._output_queue)
        self._producer.start()

    def _is_connected(self):
        return self._producer.is_connected()

    @property
    def timespan(self):
        return self._timespan / self._x_axis_zoom

    @property
    def valuespan(self):
        return self._valuespan / self._y_axis_zoom

    def run(self):
        while True:
            try:
                self.tick()
            except QuitError:
                break

            time.sleep(0.05)

    def tick(self):
        self.update()
        self.process_user_input()

        if self._modified:
            self.redraw()
            self._modified = False

    def redraw(self):
        self._stdscr.clear()

        if self._show_help:
            self.draw_help()
        else:
            self.draw_main()

        self._stdscr.refresh()

    def draw_help(self):
        margin = (self._ncols - HELP_NCOLS) // 2
        text_col_left = margin + 2
        help_lines = HELP_TEXT.splitlines()

        self.addstr_frame(
            1,
            margin,
            '┌──────────────────────────────────────────────────────────┐')
        self.addstr(1, margin + 1, ' Help ')

        for row, line in enumerate(help_lines, 2):
            self.addstr_frame(row, margin, '│')
            self.addstr_frame(row, margin + HELP_NCOLS - 1, '│')
            self.addstr(row, text_col_left, line)

        self.addstr_frame(
            len(help_lines) + 2,
            margin,
            '└──────────────────────────────────────────────────────────┘')

    def calc_x_limits(self):
        if self.is_moved():
            maximum = self._x_axis_center + self.timespan / 2
        else:
            maximum = self._x_axis_maximum

        minimum = maximum - self.timespan

        return minimum, maximum

    def calc_y_limits(self, values):
        if self.is_moved():
            y_axis_maximum = self._y_axis_center + self.valuespan / 2
            y_axis_minimum = y_axis_maximum - self.valuespan
        elif self._y_min is None and self._y_max is None:
            if values:
                minimum_value = min(values)
                maximum_value = max(values)
                delta = max(maximum_value - minimum_value, 1)
                y_axis_minimum = minimum_value - delta * 0.01
                y_axis_maximum = maximum_value + delta * 0.01
                self._y_axis_maximum = y_axis_maximum
            else:
                y_axis_minimum = 0
                y_axis_maximum = 1

            self._valuespan = y_axis_maximum - y_axis_minimum

            y_axis_minimum /= self._y_axis_zoom
            y_axis_maximum /= self._y_axis_zoom
        else:
            delta = max(self._y_max - self._y_min, 1)
            y_axis_minimum = self._y_min
            y_axis_maximum = self._y_max
            self._y_axis_maximum = y_axis_maximum
            self._valuespan = y_axis_maximum - y_axis_minimum

        decimals = (y_axis_maximum - y_axis_minimum) * (6 / (self._nrows - 2))
        decimals = int(math.floor(math.log10(decimals)))

        if decimals >= 0:
            decimals = None
        else:
            decimals = int(-decimals)

        return y_axis_minimum, y_axis_maximum, decimals

    def calc_grid_cols(self,
                       frame_col_left,
                       frame_ncols,
                       x_axis_minimum,
                       x_axis_maximum):
        alignment = x_axis_minimum % (self.timespan / 4)
        minimum = x_axis_minimum - alignment
        maximum = x_axis_maximum + alignment
        cols = []

        for i in range(1, 5):
            timestamp = minimum + self.timespan / 4 * i
            col = int(
                frame_ncols *
                (timestamp - x_axis_minimum) / (x_axis_maximum - x_axis_minimum))

            if 0 < col < frame_ncols:
                cols.append((frame_col_left + col, timestamp))

        return cols

    def data_timespan_slice(self,
                            x_axis_minimum,
                            x_axis_maximum):
        timestamps = []
        values = []
        timestamp_before_x_axis_minimim = None
        value_before_x_axis_minimim = None

        for timestamp, value in self._data:
            if value is None:
                continue

            if timestamp < x_axis_minimum:
                timestamp_before_x_axis_minimim = timestamp
                value_before_x_axis_minimim = value
            else:
                if timestamp_before_x_axis_minimim is not None:
                    timestamps.append(timestamp_before_x_axis_minimim)
                    values.append(value_before_x_axis_minimim)
                    timestamp_before_x_axis_minimim = None

                timestamps.append(timestamp)
                values.append(value)

                if timestamp > x_axis_maximum:
                    break

        return timestamps, values

    def draw_main(self):
        if self._playing and not self.is_moved():
            if self._data:
                self._x_axis_maximum = self._data[-1][0]
            else:
                self._x_axis_maximum = time.time()

        x_axis_minimum, x_axis_maximum = self.calc_x_limits()
        timestamps, values = self.data_timespan_slice(x_axis_minimum,
                                                      x_axis_maximum)
        y_axis_minimum, y_axis_maximum, y_axis_decimals = self.calc_y_limits(values)
        frame_col_left = max(len(str(math.floor(y_axis_minimum))),
                             len(str(math.ceil(y_axis_maximum))))

        if y_axis_decimals is not None:
            frame_col_left += y_axis_decimals + 1

        frame_col_left += 1
        frame_col_right = self._ncols - 1
        frame_ncols = frame_col_right - frame_col_left
        frame_nrows = self._nrows - 2
        grid_cols = self.calc_grid_cols(frame_col_left,
                                        frame_ncols,
                                        x_axis_minimum,
                                        x_axis_maximum)

        self.draw_frame(frame_col_left,
                        frame_col_right,
                        frame_ncols)

        self.draw_grid(frame_col_left,
                       frame_nrows,
                       frame_ncols,
                       grid_cols)

        self.draw_data(timestamps,
                       values,
                       frame_col_left,
                       frame_nrows,
                       frame_ncols,
                       x_axis_minimum,
                       x_axis_maximum,
                       y_axis_minimum,
                       y_axis_maximum)

        self.draw_x_axis(frame_nrows, grid_cols)

        self.draw_y_axis(frame_col_left,
                         frame_nrows,
                         y_axis_minimum,
                         y_axis_maximum,
                         y_axis_decimals)

    def draw_frame(self,
                   frame_col_left,
                   frame_col_right,
                   frame_ncols):
        self.addstr_frame(0, frame_col_left, '┌' + (frame_ncols - 1) * '─' + '┐')
        self.addstr(0, frame_col_left + 1, f' {self._config["title"]} ')

        x_zoom = zoom_number_to_text(self._x_axis_zoom)
        y_zoom = zoom_number_to_text(self._y_axis_zoom)
        zoom_text = f' {x_zoom}x,{y_zoom}x '

        if self._playing:
            playing_text = ' ▶ '
        else:
            playing_text = ' ⏸ '

        if self._is_connected():
            status_text = ' Connected '
            col = frame_col_right - len(status_text)
            self.addstr(0, col, status_text)
        else:
            status_text = ' Disconnected '
            col = frame_col_right - len(status_text)
            self.addstr_red_bold(0, col, status_text)

        col -= len(playing_text) + 1
        self.addstr(0, col, playing_text)
        col -= len(zoom_text) + 1
        self.addstr(0, col, zoom_text)

        for row in range(self._nrows - 2):
            self.addstr_frame(row + 1, frame_col_left, '│')
            self.addstr_frame(row + 1, frame_col_right, '│')

        self.addstr_frame(self._nrows - 2,
                          frame_col_left,
                          '└' + (frame_ncols - 1) * '─' + '┘')

    def draw_data(self,
                  timestamps,
                  values,
                  frame_col_left,
                  frame_nrows,
                  frame_ncols,
                  x_axis_minimum,
                  x_axis_maximum,
                  y_axis_minimum,
                  y_axis_maximum):
        if not timestamps:
            return

        canvas = irwin.Canvas(frame_ncols - 1,
                              frame_nrows - 1,
                              x_axis_minimum,
                              x_axis_maximum,
                              y_axis_minimum,
                              y_axis_maximum)
        x0 = timestamps[0]
        y0 = values[0]

        for x1, y1 in zip(timestamps[1:], values[1:]):
            canvas.draw_line(x0, y0, x1, y1)
            x0 = x1
            y0 = y1

        for row, line in enumerate(canvas.render().splitlines()):
            for mo in RE_SPLIT.finditer(line):
                self.addstr(row + 1, frame_col_left + 1 + mo.start(1), mo.group(1))

    def draw_x_axis(self, frame_nrows, grid_cols):
        for col, timestamp in grid_cols:
            self.addstr_frame(frame_nrows, col, '┼')
            self.addstr(frame_nrows + 1, col - 3, format_clock(timestamp))

    def draw_y_axis(self,
                    frame_col_left,
                    frame_nrows,
                    y_axis_minimum,
                    y_axis_maximum,
                    y_axis_decimals):
        fmt = f'{{:-{frame_col_left - 1}}}'

        for row in range(1, frame_nrows):
            if is_y_axis_grid_row(frame_nrows, row):
                self.addstr_frame(row, frame_col_left, '┼')
                value = round(y_axis_minimum
                              + (frame_nrows - row + 1)
                              * (y_axis_maximum - y_axis_minimum) / frame_nrows,
                              y_axis_decimals)
                self.addstr(row, 0, fmt.format(value))

    def draw_grid(self,
                  frame_col_left,
                  frame_nrows,
                  frame_ncols,
                  grid_cols):
        line = (frame_ncols - 1) * '╌'

        for row in range(1, frame_nrows):
            if is_y_axis_grid_row(frame_nrows, row):
                self.addstr_frame(row, frame_col_left + 1, line)

            for col, _ in grid_cols:
                self.addstr_frame(row, col, '┆')

    def addstr(self, row, col, text):
        try:
            self._stdscr.addstr(row, col, text.encode('utf-8'))
        except curses.error:
            pass

    def addstra(self, row, col, text, attr):
        try:
            self._stdscr.addstr(row, col, text.encode('utf-8'), attr)
        except curses.error:
            pass

    def addstr_red_bold(self, row, col, text):
        self.addstra(row, col, text, curses.color_pair(2) | curses.A_BOLD)

    def addstr_frame(self, row, col, text):
        self.addstra(row, col, text, curses.color_pair(1))

    def process_user_input_help(self, key):
        self._show_help = False

    def process_user_input_main(self, key):
        if key in ['h', '?']:
            self._show_help = True
        elif key == ' ':
            self._playing = not self._playing
        elif key == 'KEY_UP':
            self.ensure_moving()
            self._y_axis_center += self.valuespan / 8
        elif key == 'KEY_DOWN':
            self.ensure_moving()
            self._y_axis_center -= self.valuespan / 8
        elif key == 'KEY_LEFT':
            self.ensure_moving()
            self._x_axis_center -= self.timespan / 8
        elif key == 'KEY_RIGHT':
            self.ensure_moving()
            self._x_axis_center += self.timespan / 8
        elif key == 'r':
            self._timespan = self._config['timespan']
            self._x_axis_zoom = 1
            self._y_axis_zoom = 1
            self._x_axis_center = None
            self._y_axis_center = None
        elif key == 'c':
            self._data.clear()
            self._previous_timestamp = None
            self._previous_value = None
        elif key in ['kUP5', 'CTL_UP']:
            if self._x_axis_zoom < 16384:
                self._x_axis_zoom *= 2

                if self.is_moved():
                    self._y_axis_zoom *= 2
        elif key in ['kDN5', 'CTL_DOWN']:
            if self._x_axis_zoom > 1 / 16384:
                self._x_axis_zoom /= 2

                if self.is_moved():
                    self._y_axis_zoom /= 2

    def ensure_moving(self):
        if not self.is_moved():
            self._x_axis_center = self._x_axis_maximum - self.timespan / 2
            self._y_axis_center = self._y_axis_maximum - self.valuespan / 2

    def is_moved(self):
        if self._x_axis_center is not None:
            return True

        if self._y_axis_center is not None:
            return True

        return False

    def process_user_input(self):
        while True:
            try:
                key = self._stdscr.getkey()
            except curses.error:
                break

            self._modified = True

            if key == 'q':
                raise QuitError()

            if self._show_help:
                self.process_user_input_help(key)
            else:
                self.process_user_input_main(key)

    def process_data(self, timestamp, output):
        if output is None:
            value = None
        else:
            output = output.decode()

            mo = self._re_value.search(output)

            if not mo:
                raise Exception(
                    f"Pattern '{self._config['pattern']}' does not match command "
                    f"output '{output}'.")

            value = float(mo.group(1))

            if self._algorithm == 'delta':
                previous_value = self._previous_value
                self._previous_value = value

                if self._previous_timestamp is None:
                    value = None
                else:
                    value -= previous_value
                    value /= (timestamp - self._previous_timestamp)

                self._previous_timestamp = timestamp

            if value is not None:
                value *= self._scale
                value += self._offset

                if self._y_lower_limit is not None:
                    value = max(value, self._y_lower_limit)

                if self._y_upper_limit is not None:
                    value = min(value, self._y_upper_limit)

        self._data.append((timestamp, value))
        self._modified = True

    def update_data(self):
        try:
            while True:
                self.process_data(*self._output_queue.get_nowait())
        except queue.Empty:
            pass

    def update(self):
        if self._playing and not self._show_help:
            self.update_data()

        if curses.is_term_resized(self._nrows, self._ncols):
            self._nrows, self._ncols = self._stdscr.getmaxyx()
            self._modified = True


def _do_plot(args):
    config = load_config(os.path.expanduser('~/.bunga-plot.json'),
                         args.name)

    def plot(stdscr):
        Plot(stdscr, config, args).run()

    try:
        curses.wrapper(plot)
    except KeyboardInterrupt:
        pass


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'plot',
        description='Plot any command output over time.')
    subparser.add_argument('-u' ,'--uri',
                           default='tcp://127.0.0.1:28000',
                           help='URI of the server (default: %(default)s)')
    subparser.add_argument('name', help='Plot name.')
    subparser.set_defaults(func=_do_plot)
