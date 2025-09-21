import unittest
from typing import *

from scaevola.core import Scaevola


class TestScaevolaDocstrings(unittest.TestCase):
    def test_methods_have_docstrings(self: Self) -> None:
        methods_to_check = [
            "__ge__",
            "__gt__",
            "__radd__",
            "__rand__",
            "__rdivmod__",
            "__rfloordiv__",
            "__rlshift__",
            "__rmatmul__",
            "__rmod__",
            "__rmul__",
            "__ror__",
            "__rpow__",
            "__rrshift__",
            "__rsub__",
            "__rtruediv__",
            "__rxor__",
        ]

        for name in methods_to_check:
            with self.subTest(method=name):
                magic = getattr(Scaevola, name, None)
                self.assertTrue(
                    magic.__doc__.startswith("This magic method "),
                    "doc=%r" % magic.__doc__,
                )


if __name__ == "__main__":
    unittest.main()
