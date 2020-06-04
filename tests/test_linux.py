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
        formatted = linux.format_ps([
            'Name:	init\n'
            'Umask:	0022\n'
            'State:	S (sleeping)\n'
            'Tgid:	1\n'
            'Ngid:	0\n'
            'Pid:	1\n'
            'PPid:	0\n'
            'TracerPid:	0\n'
            'Uid:	0	0	0	0\n'
            'Gid:	0	0	0	0\n'
            'FDSize:	256\n'
            'Groups:	 \n'
            'VmPeak:	   16544 kB\n'
            'VmSize:	    8348 kB\n'
            'VmLck:	       0 kB\n'
            'VmPin:	       0 kB\n'
            'VmHWM:	   15096 kB\n'
            'VmRSS:	    6900 kB\n'
            'RssAnon:	    6308 kB\n'
            'RssFile:	     592 kB\n'
            'RssShmem:	       0 kB\n'
            'VmData:	    7300 kB\n'
            'VmStk:	     132 kB\n'
            'VmExe:	     840 kB\n'
            'VmLib:	       8 kB\n'
            'VmPTE:	      12 kB\n'
            'VmPMD:	       0 kB\n'
            'VmSwap:	       0 kB\n'
            'Threads:	9\n'
            'SigQ:	0/7532\n'
            'SigPnd:	0000000000000000\n'
            'ShdPnd:	0000000000000000\n'
            'SigBlk:	0000000000000000\n'
            'SigIgn:	0000000000000000\n'
            'SigCgt:	0000000000000000\n'
            'CapInh:	0000000000000000\n'
            'CapPrm:	0000003fffffffff\n'
            'CapEff:	0000003fffffffff\n'
            'CapBnd:	0000003fffffffff\n'
            'CapAmb:	0000000000000000\n'
            'NoNewPrivs:	0\n'
            'Seccomp:	0\n'
            'Speculation_Store_Bypass:	unknown\n'
            'Cpus_allowed:	1\n'
            'Cpus_allowed_list:	0\n'
            'voluntary_ctxt_switches:	3925\n'
            'nonvoluntary_ctxt_switches:	10\n',
            'Name:	ml_worker_pool\n'
            'Umask:	0022\n'
            'State:	S (sleeping)\n'
            'Tgid:	1\n'
            'Ngid:	0\n'
            'Pid:	36\n'
            'PPid:	0\n'
            'TracerPid:	0\n'
            'Uid:	0	0	0	0\n'
            'Gid:	0	0	0	0\n'
            'FDSize:	256\n'
            'Groups:	 \n'
            'VmPeak:	   16544 kB\n'
            'VmSize:	    8348 kB\n'
            'VmLck:	       0 kB\n'
            'VmPin:	       0 kB\n'
            'VmHWM:	   15096 kB\n'
            'VmRSS:	    6900 kB\n'
            'RssAnon:	    6308 kB\n'
            'RssFile:	     592 kB\n'
            'RssShmem:	       0 kB\n'
            'VmData:	    7300 kB\n'
            'VmStk:	     132 kB\n'
            'VmExe:	     840 kB\n'
            'VmLib:	       8 kB\n'
            'VmPTE:	      12 kB\n'
            'VmPMD:	       0 kB\n'
            'VmSwap:	       0 kB\n'
            'Threads:	9\n'
            'SigQ:	0/7532\n'
            'SigPnd:	0000000000000000\n'
            'ShdPnd:	0000000000000000\n'
            'SigBlk:	0000000000000000\n'
            'SigIgn:	0000000000000000\n'
            'SigCgt:	0000000000000000\n'
            'CapInh:	0000000000000000\n'
            'CapPrm:	0000003fffffffff\n'
            'CapEff:	0000003fffffffff\n'
            'CapBnd:	0000003fffffffff\n'
            'CapAmb:	0000000000000000\n'
            'NoNewPrivs:	0\n'
            'Seccomp:	0\n'
            'Speculation_Store_Bypass:	unknown\n'
            'Cpus_allowed:	1\n'
            'Cpus_allowed_list:	0\n'
            'voluntary_ctxt_switches:	208\n'
            'nonvoluntary_ctxt_switches:	9141\n'
        ])

        self.assertEqual(
            formatted,
            'NAME               STATE     SCHEDULED\n'
            '--------------------------------------\n'
            'init               sleeping  3935\n'
            'ml_worker_pool     sleeping  9349\n')
