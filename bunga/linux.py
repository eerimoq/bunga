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


def format_ps(proc_n_status):
    lines = [
        'NAME               STATE     SCHEDULED',
        '--------------------------------------'
    ]

    for status in proc_n_status:
        name = '-'
        state = '-'
        scheduled = 0

        for line in status.splitlines():
            if line.startswith('Name:'):
                name = line.split()[-1]
            elif line.startswith('State:'):
                state = line.partition('(')[2].partition(')')[0]
            elif line.startswith('voluntary_ctxt_switches:'):
                scheduled += int(line.split()[-1])
            elif line.startswith('nonvoluntary_ctxt_switches:'):
                scheduled += int(line.split()[-1])

        lines.append(f'{name:18} {state:9} {scheduled}')

    return '\n'.join(lines) + '\n'
