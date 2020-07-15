import os
import threading
import re
import time
import curses
from datetime import datetime
import plotille
import queue
import math
import json


DEFAULT_CONFIG = {
    'temperature': {
        'title': 'Temperature [C]',
        'command': 'ds18b20 read 28000013423433',
        'pattern': '^(\d+\.\d+)',
        'interval': 5,
        'timespan': 60
    }
}

HELP_FMT = '''\
Quit: q or <Ctrl-C>
Pause: <Space>
Grid: g
Move: <Left> and <Right>
Zoom: <Up> and <Down>
Clear: c
Help: h or ?\
'''

HELP_NCOLS = 60

RE_SPLIT = re.compile(r'⠀*([^⠀]+)')


def format_clock(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')


class Producer(threading.Thread):

    def __init__(self, config, data_queue):
        super().__init__()
        self._data_queue = data_queue
        self.daemon = True
        self._interval = config['interval']
        self._x = 0

    def run(self):
        while True:
            self._data_queue.put((time.time(), 10 + 30 * math.sin(self._x)))
            self._x += 0.2
            time.sleep(self._interval)


class QuitError(Exception):
    pass


def load_config(path, name):
    if os.path.isfile(path):
        with open(path, 'r') as fin:
            config = json.load(fin)
    else:
        config = DEFAULT_CONFIG

    try:
        config = config[name]
    except KeyError:
        raise Exception(f"Monitor '{name}' not found.")

    if config['interval'] < 1:
        raise Exception('Interval must be at least one.')

    if config['timespan'] < 1:
        raise Exception('Timespan must be at least one.')

    config['pattern'] = re.compile(config['pattern'])

    return config


class Monitor:

    def __init__(self, stdscr, config, args):
        self._config = config
        self._stdscr = stdscr
        self._data_queue = queue.Queue()
        self._nrows, self._ncols = stdscr.getmaxyx()
        self._modified = True
        self._show_help = False
        self._playing = True
        self._grid = True
        self._connected = True
        self._timestamps = []
        self._values = []
        self._timespan = config['timespan']
        self._x_axis_offset = None
        self._timestamp = time.time()

        stdscr.keypad(True)
        stdscr.nodelay(True)
        curses.use_default_colors()
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_RED, -1)
        curses.init_pair(3, curses.COLOR_GREEN, -1)

        self._producer = Producer(config, self._data_queue)
        self._producer.start()

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
        help_lines = HELP_FMT.splitlines()

        self.add_frame(
            1,
            margin,
            '┌──────────────────────────────────────────────────────────┐')
        self.addstr(1, margin + 1, ' Help ')

        for row, line in enumerate(help_lines, 2):
            self.add_frame(row, margin, '│')
            self.add_frame(row, margin + HELP_NCOLS - 1, '│')
            self.addstr(row, text_col_left, line)

        self.add_frame(
            len(help_lines) + 2,
            margin,
            '└──────────────────────────────────────────────────────────┘')

    def draw_main(self):
        if self._values:
            frame_col_left = max(len(str(round(min(self._values)))),
                                 len(str(round(max(self._values)))))
            frame_col_left += 1
        else:
            frame_col_left = 3

        frame_col_right = self._ncols - 1
        frame_ncols = frame_col_right - frame_col_left
        frame_row_top = 0
        frame_row_bottom = self._nrows - 2
        frame_nrows = frame_row_bottom - frame_row_top

        self.draw_frame(frame_row_top,
                        frame_col_left,
                        frame_col_right,
                        frame_ncols)

        if self._playing:
            self._timestamp = time.time()

        x_axis_maximum = self._timestamp

        if self._x_axis_offset is not None:
            x_axis_maximum += self._x_axis_offset

        x_axis_minimum = x_axis_maximum - self._timespan

        if self._grid:
            self.draw_grid(frame_col_left,
                           frame_nrows,
                           frame_ncols,
                           x_axis_minimum,
                           x_axis_maximum)

        if self._timestamps:
            self.draw_data(frame_col_left,
                           frame_nrows,
                           frame_ncols,
                           x_axis_minimum,
                           x_axis_maximum)

        self.draw_x_axis(frame_col_left,
                         frame_nrows,
                         frame_ncols,
                         x_axis_minimum,
                         x_axis_maximum)

    def draw_frame(self,
                   frame_row_top,
                   frame_col_left,
                   frame_col_right,
                   frame_ncols):
        self.add_frame(frame_row_top, frame_col_left, '┌' + (frame_ncols - 1) * '─' + '┐')
        self.addstr(frame_row_top, frame_col_left + 1, f' {self._config["title"]} ')

        if self._connected:
            self.addstr_green(frame_row_top, frame_col_right - 11, ' Connected ')
        else:
            self.addstr_red_bold(frame_row_top, frame_col_right - 14, ' Disconnected ')

        for row in range(self._nrows - 2):
            self.add_frame(row + 1, frame_col_left, '│')
            self.add_frame(row + 1, frame_col_right, '│')

        self.add_frame(self._nrows - 2, frame_col_left, '└' + (frame_ncols - 1) * '─' + '┘')

    def draw_data(self,
                  frame_col_left,
                  frame_nrows,
                  frame_ncols,
                  x_axis_minimum,
                  x_axis_maximum):
        minimum_value = min(self._values)
        maximum_value = max(self._values)
        delta = max(maximum_value - minimum_value, 1)
        y_axis_minimum = minimum_value - delta * 0.1
        y_axis_maximum = maximum_value + delta * 0.1

        plot = plotille.plot(self._timestamps,
                             self._values,
                             height=frame_nrows - 2,
                             width=frame_ncols - 1,
                             x_min=x_axis_minimum,
                             x_max=x_axis_maximum,
                             y_min=y_axis_minimum,
                             y_max=y_axis_maximum,
                             origin=False)

        for row, line in enumerate(plot.splitlines()[1:-2]):
            y, _, line = line.partition('|')

            if ((frame_nrows - row - 5) % 6) == 0:
                self.addstr(row + 1, 0, str(round(float(y))))

            for mo in RE_SPLIT.finditer(line[1:]):
                self.addstr(row + 1, frame_col_left + 1 + mo.start(1), mo.group(1))

    def draw_x_axis(self,
                    frame_col_left,
                    frame_nrows,
                    frame_ncols,
                    x_axis_minimum,
                    x_axis_maximum):
        for row in range(frame_nrows):
            if ((frame_nrows - row - 5) % 6) == 0:
                self.add_frame(row + 1, frame_col_left, '┼')

        alignment = x_axis_minimum % (self._timespan // 4)
        minimum = int(x_axis_minimum - alignment)
        maximum = int(x_axis_maximum + alignment)

        for timestamp in range(minimum, maximum, self._timespan // 4):
            col = int(frame_ncols *
                      (timestamp - x_axis_minimum) / (x_axis_maximum - x_axis_minimum))

            if 0 < col < frame_ncols:
                self.add_frame(frame_nrows, frame_col_left + col, '┼')
                self.addstr(frame_nrows + 1,
                            frame_col_left + col - 3,
                            format_clock(timestamp))

    def draw_grid(self,
                  frame_col_left,
                  frame_nrows,
                  frame_ncols,
                  x_axis_minimum,
                  x_axis_maximum):
        line = (frame_ncols - 1) * '╌'
        alignment = x_axis_minimum % (self._timespan // 4)
        minimum = int(x_axis_minimum - alignment)
        maximum = int(x_axis_maximum + alignment)

        for row in range(1, frame_nrows):
            if ((frame_nrows - row - 4) % 6) == 0:
                self.add_frame(row, frame_col_left + 1, line)

            for timestamp in range(minimum, maximum, self._timespan // 4):
                col = int(frame_ncols *
                          (timestamp - x_axis_minimum) / (x_axis_maximum - x_axis_minimum))

                if 0 < col < frame_ncols:
                    self.add_frame(row, frame_col_left + col, '┆')

    def addstr(self, row, col, text):
        try:
            self._stdscr.addstr(row, col, text.encode('utf-8'))
        except curses.error:
            pass

    def addstr_red_bold(self, row, col, text):
        try:
            self._stdscr.addstr(row,
                                col,
                                text.encode('utf-8'),
                                curses.color_pair(2) | curses.A_BOLD)
        except curses.error:
            pass

    def addstr_green(self, row, col, text):
        try:
            self._stdscr.addstr(row,
                                col,
                                text.encode('utf-8'),
                                curses.color_pair(3))
        except curses.error:
            pass

    def add_frame(self, row, col, text):
        try:
            self._stdscr.addstr(row, col, text.encode('utf-8'), curses.color_pair(1))
        except curses.error:
            pass

    def process_user_input_help(self, key):
        self._show_help = False

    def process_user_input_main(self, key):
        if key in ['h', '?']:
            self._show_help = True
        elif key == ' ':
            self._playing = not self._playing
        elif key == 'g':
            self._grid = not self._grid
        elif key == 'KEY_UP':
            if self._timespan >= 20:
                self._timespan = int(self._timespan / 2)

                if self._x_axis_offset is not None:
                    self._x_axis_offset -= self._timespan / 2
        elif key == 'KEY_DOWN':
            if self._x_axis_offset is not None:
                self._x_axis_offset += self._timespan / 2

            self._timespan *= 2
        elif key == 'KEY_LEFT':
            if self._x_axis_offset is None:
                self._x_axis_offset = 0

            self._x_axis_offset -= self._timespan / 8
        elif key == 'KEY_RIGHT':
            if self._x_axis_offset is None:
                self._x_axis_offset = 0

            self._x_axis_offset += self._timespan / 8
        elif key == 'r':
            self._timespan = self._config['timespan']
            self._x_axis_offset = None
        elif key == 'c':
            self._timestamps = []
            self._values = []

    def process_user_input(self):
        try:
            key = self._stdscr.getkey()
        except curses.error:
            return

        self._modified = True

        if key == 'q':
            raise QuitError()

        if self._show_help:
            self.process_user_input_help(key)
        else:
            self.process_user_input_main(key)

    def update_data(self):
        try:
            while True:
                timestamp, value = self._data_queue.get_nowait()
                self._timestamps.append(timestamp)
                self._values.append(value)
                self._modified = True
        except queue.Empty:
            pass

    def update(self):
        if self._playing:
            self.update_data()

        if curses.is_term_resized(self._nrows, self._ncols):
            self._nrows, self._ncols = self._stdscr.getmaxyx()


def _do_monitor(args):
    config = load_config('bunga-monitor.json', args.name)

    def monitor(stdscr):
        Monitor(stdscr, config, args).run()

    try:
        curses.wrapper(monitor)
    except KeyboardInterrupt:
        pass


def add_subparser(subparsers):
    subparser = subparsers.add_parser('monitor')
    subparser.add_argument('-u' ,'--uri',
                           default='tcp://127.0.0.1:28000',
                           help='URI of the server (default: %(default)s)')
    subparser.add_argument('name', help='Monitor name.')
    subparser.set_defaults(func=_do_monitor)
