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

    def test_uptime(self):
        formatted = linux.format_uptime('19747.42 19696.08\n',
                                        '0.49 0.45 0.46 3/35 102\n')

        self.assertEqual(
            formatted,
            'up 5 hours, 29 minutes and 7 seconds,  load average: 0.49, 0.45, '
            '0.46\n')

    def test_ps(self):
        formatter = linux.PsFormatter()
        formatted = formatter.format(
            'cpu  4812 0 859 177717 0 0 97 0 0 0',
            [
                '49 (bunga_server) S 0 0 0 0 -1 4194368 735 0 0 0 74 241 0 0 20 0 '
                '9 0 248 5316608 930 4294967295 65536 923972 3196878608 0 0 0 0 0 '
                '0 1 0 0 -1 0 0 0 0 0 0 991224 991996 1011712 3196878814 3196878820 '
                '3196878820 3196878838 0',
                '36 (ml_worker_pool) S 0 0 0 0 -1 1077936192 2080 0 0 0 334 24 0 0 '
                '20 0 9 0 29 5316608 930 4294967295 65536 923972 3196878608 0 0 0 0 '
                '0 0 1 0 0 -1 0 0 0 0 0 0 991224 991996 1011712 3196878814 3196878820 '
                '3196878820 3196878838 0'
            ])

        self.assertEqual(
            formatted,
            'NAME               PID  STATE     CPU-TICKS  CPU-DELTA\n'
            '------------------------------------------------------\n'
            'bunga_server       49   sleeping  315        -\n'
            'ml_worker_pool     36   sleeping  358        -\n'
            'idle               -    -         177717     -\n')

        formatted = formatter.format(
            'cpu  4812 0 859 178717 0 0 97 0 0 0',
            [
                '49 (bunga_server) R 0 0 0 0 -1 4194368 735 0 0 0 88 250 0 0 20 0 '
                '9 0 248 5316608 930 4294967295 65536 923972 3196878608 0 0 0 0 0 '
                '0 0 0 0 -1 0 0 0 0 0 0 991224 991996 1011712 3196878814 3196878820 '
                '3196878820 3196878838 0',
                '36 (ml_worker_pool) S 0 0 0 0 -1 1077936192 2080 0 0 0 334 24 0 0 '
                '20 0 9 0 29 5316608 930 4294967295 65536 923972 3196878608 0 0 0 0 '
                '0 0 1 0 0 -1 0 0 0 0 0 0 991224 991996 1011712 3196878814 3196878820 '
                '3196878820 3196878838 0',
                '42 (ml_shell) S 0 0 0 0 -1 4194368 0 0 0 0 0 0 0 0 20 0 9 0 30 '
                '5316608 930 4294967295 65536 923972 3196878608 0 0 0 0 0 0 1 0 0 '
                '-1 0 0 0 0 0 0 991224 991996 1011712 3196878814 3196878820 '
                '3196878820 3196878838 0'
            ])

        self.assertEqual(
            formatted,
            'NAME               PID  STATE     CPU-TICKS  CPU-DELTA\n'
            '------------------------------------------------------\n'
            'bunga_server       49   running   338        23\n'
            'ml_worker_pool     36   sleeping  358        0\n'
            'ml_shell           42   sleeping  0          -\n'
            'idle               -    -         178717     1000\n')
