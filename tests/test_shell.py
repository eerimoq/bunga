import unittest

import bunga.subparsers.shell as shell


class ShelltTest(unittest.TestCase):

    def test_parse_command(self):
        datas = [
            ('', ('', '')),
            ('ls | grep foo', ('ls', 'grep foo')),
            ('cat /root/conf > conf', ('cat /root/conf', 'cat > conf')),
            ('ls | grep foo > log', ('ls', 'grep foo > log'))
        ]

        for line, expected in datas:
            self.assertEqual(shell.parse_command(line), expected)
