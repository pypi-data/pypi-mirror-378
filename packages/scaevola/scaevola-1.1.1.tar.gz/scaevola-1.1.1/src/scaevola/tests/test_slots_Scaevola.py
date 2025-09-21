import unittest
from typing import *

from scaevola.core import Scaevola


class Foo(Scaevola):
    __slots__ = ("x", "y")


class Bar(Scaevola):
    pass


class TestSlots(unittest.TestCase):
    def test_foo(self: Self) -> None:
        foo: Foo = Foo()
        foo.x = 4
        foo.y = 2
        foo.z = 0
        self.assertEqual(foo.x, 4)
        self.assertEqual(foo.y, 2)
        self.assertEqual(foo.z, 0)

    def test_bar(self: Self) -> None:
        bar: Bar = Bar()
        bar.x = 4
        bar.y = 2
        self.assertEqual(bar.x, 4)
        self.assertEqual(bar.y, 2)


if __name__ == "__main__":
    unittest.main()
