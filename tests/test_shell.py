import unittest
from unittest.mock import patch
from unittest.mock import Mock
from unittest.mock import call
from io import StringIO

import bunga
import bunga.subparsers.shell as shell

from .utils import start_server


class Client:

    def __init__(self):
        self.execute_command = Mock()
        self.wait_for_connection = Mock()


class ShellTest(unittest.TestCase):

    maxDiff = None

    def test_parse_command(self):
        datas = [
            ('', ('', '')),
            ('ls | grep foo', ('ls', 'grep foo')),
            ('cat /root/conf > conf', ('cat /root/conf', 'cat > conf')),
            ('ls | grep foo > log', ('ls', 'grep foo > log'))
        ]

        for line, expected in datas:
            self.assertEqual(shell.parse_command(line), expected)

    def execute_commands_comment_handler(self, client):
        client.close()

    @patch('prompt_toolkit.prompt')
    def test_execute_command_comment(self, prompt):
        prompt.side_effect = [
            '# A comment',
            'exit'
        ]
        client = Client()
        client.execute_command.side_effect = [
            b'\nCommands\n'
        ]

        shell.shell_main(client)

    # ToDo: Move to client tests.
    @patch('prompt_toolkit.prompt')
    def _test_execute_command_netstat(self, prompt):
        prompt.side_effect = [
            'netstat',
            'exit'
        ]
        client = Client()
        client.execute_command.side_effect = [
            b'\nCommands\n',
            b'   0: 00000000:6D60 00000000:0000 0A 00000000:00000000 00:00000000 '
            b'00000000     0        0 2006 1 eee68000 100 0 0 10 0\n'
        ]
        stdout = StringIO()

        with patch('sys.stdout', stdout):
            shell.shell_main(client)

        self.assertEqual(client.execute_command.call_args_list,
                         [
                             call('help'),
                             call('cat /proc/net/tcp')
                         ])
        self.assertIn(
            'PROTO  LOCAL-ADDRESS          REMOTE-ADDRESS         STATE\n'
            '----------------------------------------------------------------\n'
            'tcp    0.0.0.0:28000          0.0.0.0:0              listen\n',
            stdout.getvalue())

    @patch('prompt_toolkit.prompt')
    def _test_execute_command_uptime(self, prompt):
        prompt.side_effect = [
            'uptime',
            'exit'
        ]
        client = Client()
        client.execute_command.side_effect = [
            b'\nCommands\n',
            b'19747.42 19696.08\n',
            b'0.49 0.45 0.46 3/35 102\n'
        ]
        stdout = StringIO()

        with patch('sys.stdout', stdout):
            shell.shell_main(client)

        self.assertEqual(client.execute_command.call_args_list,
                         [
                             call('help'),
                             call('cat /proc/uptime'),
                             call('cat /proc/loadavg')
                         ])
        self.assertIn(
            'up 5 hours, 29 minutes and 7 seconds,  load average: 0.49, 0.45, '
            '0.46\n',
            stdout.getvalue())

    @patch('prompt_toolkit.prompt')
    def _test_execute_command_ps(self, prompt):
        prompt.side_effect = [
            'ps',
            'exit'
        ]
        client = Client()
        client.execute_command.side_effect = [
            b'\nCommands\n',
            b'36 49',
            b'36 (ml_worker_pool) S 0 0 0 0 -1 1077936192 2080 0 0 0 334 24 0 0 '
            b'20 0 9 0 29 5316608 930 4294967295 65536 923972 3196878608 0 0 0 0 '
            b'0 0 1 0 0 -1 0 0 0 0 0 0 991224 991996 1011712 3196878814 3196878820 '
            b'3196878820 3196878838 0',
            b'49 (bunga_server) S 0 0 0 0 -1 4194368 735 0 0 0 74 241 0 0 20 0 '
            b'9 0 248 5316608 930 4294967295 65536 923972 3196878608 0 0 0 0 0 '
            b'0 1 0 0 -1 0 0 0 0 0 0 991224 991996 1011712 3196878814 3196878820 '
            b'3196878820 3196878838 0',
            b'cpu  4812 0 859 177717 0 0 97 0 0 0'
        ]
        stdout = StringIO()

        with patch('sys.stdout', stdout):
            shell.shell_main(client)

        self.assertEqual(client.execute_command.call_args_list,
                         [
                             call('help'),
                             call('ls /proc/1/task'),
                             call('cat /proc/1/task/36/stat'),
                             call('cat /proc/1/task/49/stat'),
                             call('cat /proc/stat')
                         ])
        self.assertIn(
            'NAME               PID  STATE     CPU-TICKS  CPU-DELTA\n'
            '------------------------------------------------------\n'
            'ml_worker_pool     36   sleeping  358        -\n'
            'bunga_server       49   sleeping  315        -\n'
            'idle               -    -         177717     -\n',
            stdout.getvalue())

    @patch('prompt_toolkit.prompt')
    def test_execute_command_dmesg(self, prompt):
        prompt.side_effect = [
            'dmesg',
            'exit'
        ]
        client = Client()
        client.execute_command.side_effect = [
            b'\nCommands\n',
            b'[    3.715374] random: fast init done'
        ]
        stdout = StringIO()

        with patch('sys.stdout', stdout):
            shell.shell_main(client)

        self.assertEqual(client.execute_command.call_args_list,
                         [
                             call('help'),
                             call('dmesg')
                         ])
        self.assertIn('\x1b[32m[    3.715374]\x1b[0m random: fast init done\n',
                      stdout.getvalue())

    @patch('prompt_toolkit.prompt')
    def test_execute_command_remote(self, prompt):
        prompt.side_effect = [
            'date',
            'exit'
        ]
        client = Client()
        client.execute_command.side_effect = [
            b'\nCommands\n',
            b'2021'
        ]
        stdout = StringIO()

        with patch('sys.stdout', stdout):
            shell.shell_main(client)

        self.assertEqual(client.execute_command.call_args_list,
                         [
                             call('help'),
                             call('date')
                         ])
        self.assertIn('2021', stdout.getvalue())

    @patch('prompt_toolkit.prompt')
    def test_execute_command_error(self, prompt):
        prompt.side_effect = [
            'bad',
            'exit'
        ]
        client = Client()
        client.execute_command.side_effect = [
            b'\nCommands\n',
            bunga.ExecuteCommandError('bad', b'', 'Bad command.')
        ]
        stdout = StringIO()

        with patch('sys.stdout', stdout):
            shell.shell_main(client)

        self.assertEqual(client.execute_command.call_args_list,
                         [
                             call('help'),
                             call('bad')
                         ])
        self.assertIn('ERROR(Bad command.)', stdout.getvalue())

    def test_load_commands(self):
        client = Client()
        client.execute_command.side_effect = [
            b'\n'
            b'Commands\n'
            b'\n'
            b'          cat   Print a file.\n'
            b'         date   Print current date.\n'
            b'           dd   File copy.\n'
        ]

        self.assertEqual(shell.load_commands(client),
                         [
                             'cat',
                             'date',
                             'dd',
                             'dmesg',
                             'netstat',
                             'ps',
                             'uptime'
                         ])
