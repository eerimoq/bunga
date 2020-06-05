import re
import struct
from humanfriendly import format_timespan


RE_IPV4 = re.compile(
    r'^\s*\d+: (\w{8}):(\w{4}) (\w{8}):(\w{4}) (\w{2}) (\w{8}):(\w{8})',
    re.MULTILINE)

TCP_STATES = [
    '',
    'established',
    'syn-sent',
    'syn-recv',
    'fin-wait1',
    'fin-wait2',
    'time-wait',
    'close',
    'close-wait',
    'last-ack',
    'listen',
    'closing',
    'unknown'
]


def format_ipv4(hexstring):
    address = struct.unpack('<I', bytes.fromhex(hexstring))[0]

    return '{}.{}.{}.{}'.format((address >> 24) & 0xff,
                                (address >> 16) & 0xff,
                                (address >> 8) & 0xff,
                                (address >> 0) & 0xff)


def format_port(hexstring):
    return str(struct.unpack('>H', bytes.fromhex(hexstring))[0])


def format_netstat(proc_net_tcp):
    lines = [
        'PROTO  LOCAL-ADDRESS          REMOTE-ADDRESS         STATE',
        '----------------------------------------------------------------'
    ]

    for entry in RE_IPV4.finditer(proc_net_tcp):
        local = f'{format_ipv4(entry.group(1))}:{format_port(entry.group(2))}'
        remote = f'{format_ipv4(entry.group(3))}:{format_port(entry.group(4))}'
        state = TCP_STATES[int(entry.group(5), 16)]
        lines.append(f'tcp    {local:21}  {remote:21}  {state}')

    return '\n'.join(lines) + '\n'


def format_uptime(proc_uptime, proc_loadavg):
    one, five, fifteen, _, _ = proc_loadavg.split()
    uptime = int(float(proc_uptime.split()[0]))

    return f'up {format_timespan(uptime)},  load average: {one}, {five}, {fifteen}\n'


def proc_state(state):
    try:
        return {
            'R': 'running',
            'S': 'sleeping',
            'Z': 'zombie',
            'T': 'stopped',
            't': 'stop',
            'X': 'dead'
        }[state]
    except KeyError:
        return state


def format_thread(name, pid, state, ticks, delta):
    return f'{name:18} {str(pid):4} {state:9} {str(ticks):10} {str(delta)}'


class PsFormatter:

    def __init__(self):
        self._prev_idle_ticks = None
        self._prev_ticks = {}

    def format(self, proc_stat, proc_n_stat):
        lines = [
            'NAME               PID  STATE     CPU-TICKS  CPU-DELTA',
            '------------------------------------------------------'
        ]

        for stat in proc_n_stat:
            items = stat.split()
            pid = items[0]
            name = items[1][1:-1]
            state = proc_state(items[2])
            utime = int(items[13])
            stime = int(items[14])
            ticks = utime + stime

            try:
                delta = (ticks - self._prev_ticks[pid])
            except KeyError:
                delta = '-'

            self._prev_ticks[pid] = ticks
            lines.append(format_thread(name, pid, state, ticks, delta))

        # Faked idle thread.
        ticks = int(proc_stat.split()[4])

        if self._prev_idle_ticks is not None:
            delta = (ticks - self._prev_idle_ticks)
        else:
            delta = '-'

        self._prev_idle_ticks = ticks
        lines.append(format_thread('idle', '-', '-', ticks, delta))

        return '\n'.join(lines) + '\n'
