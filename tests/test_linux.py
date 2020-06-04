import unittest

import bunga.linux as linux


class LinuxTest(unittest.TestCase):

    def test_netstat(self):
        proc_net_tcp = (
            '   0: 00000000:6D60 00000000:0000 0A 00000000:00000000 00:00000000 '
            '00000000     0        0 2006 1 eee68000 100 0 0 10 0\n'
            '   7: 0400A8C0:C50C 0300A8C0:6D60 01 00000000:00000000 00:00000000 '
            '00000000  1000        0 44434359 1 0000000000000000 20 4 30 4 -1\n'
            '  23: 0400A8C0:C50A 0300A8C0:6D60 06 00000000:00000000 03:000016C5 '
            '00000000     0        0 0 3 0000000000000000\n'
        )

        formatted = linux.format_netstat(proc_net_tcp)

        self.assertEqual(
            formatted,
            'PROTO  LOCAL-ADDRESS          REMOTE-ADDRESS         STATE\n'
            '----------------------------------------------------------------\n'
            'tcp    0.0.0.0:28000          0.0.0.0:0              listen\n'
            'tcp    192.168.0.4:50444      192.168.0.3:28000      established\n'
            'tcp    192.168.0.4:50442      192.168.0.3:28000      time-wait\n')

    def test_netstat(self):
        formatted = linux.format_uptime('19747.42 19696.08\n',
                                        '0.49 0.45 0.46 3/35 102\n')

        self.assertEqual(
            formatted,
            'up 5 hours, 29 minutes and 7 seconds,  load average: 0.49, 0.45, 0.46\n')
