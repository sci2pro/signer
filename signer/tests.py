import io
import shlex
import sys
import unittest

from ops import parse_args


class TestParser(unittest.TestCase):
    def test_valid_font_colour(self):
        sys.stderr = io.StringIO()
        sys.argv = shlex.split(f"signer label -n file.csv -t template.png -F font.ttf -C '#abcdef'")
        args = parse_args()
        self.assertEqual(args.font_colour, "#abcdef")

    def test_invalid_font_colour(self):
        sys.stderr = io.StringIO()
        sys.argv = shlex.split(f"signer label -n file.csv -t template.png -F font.ttf -C 'nothing'")
        parse_args()
        self.assertRegex(sys.stderr.getvalue(), r"^Invalid font colour.*")
