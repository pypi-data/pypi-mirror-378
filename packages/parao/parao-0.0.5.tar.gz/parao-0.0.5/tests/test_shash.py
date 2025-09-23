from binascii import b2a_hex
from collections import OrderedDict
import sys
from types import ModuleType
from unittest import TestCase
from unittest.mock import Mock, patch

from parao.shash import (
    _SHash,
    UnsupportedError,
    UsesLocalsError,
    UsesMainWarning,
    UsesPickleWarning,
    bin_hash,
    hex_hash,
)


def fake_main_func(): ...


fake_main_func.__module__ = "__main__"


class Unpickable:
    __reduce__ = None


list_in_self = []
list_in_self.append(list_in_self)

value2expected = [
    (1, b"6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b"),
    (1.234, b"00a4e3d579394c0826980361ff3ca00e4915d0dc33b3bcb8775453aed9e8b16d"),
    (5.678j, b"2852241032ed1e4fba97014e64f3e1935f2a9eaa2093755590f851583bfb0377"),
    ("foo", b"af693da41462ec24753ce51403bd1ee5b500cd6941f62f3c97456dd8ffa7f952"),
    (b"bar", b"0f0cd6bc85f1855d43efd8f861ecd52a7a9360b7cd32537c85118e24d657abae"),
    (None, b"dc937b59892604f5a86ac96936cd7ff09e25f18ae6b758e8014a24c7fa039e91"),
    (Ellipsis, b"4637e99b28a1ce112e8f4009dbf144f3a75a04d3e4b0c30b084aef21c5e3cfe6"),
    ((1, 2, 3), b"e45859a8f662a552e3f3b3194e1e9957ac711422939adccb8d0821d299262336"),
    ([1, 2, 3], b"8e8be76c77fe4142b767006751320e33e9544becc298f50a64f5a5fc539a024a"),
    ({1, 2, 3}, b"13e72599b081ec70bc81b345e4a0c1b6051fb82cecd1bf826afea2e47a05f8d3"),
    ({1: 2, 3: 4}, b"b50bba3f366c0d96c8eb25148429c7040a004ac25d57cd131c63d25e5eeb3cb7"),
    (
        OrderedDict({1: 2, 3: 4}),
        b"a5fd8b9a41cdf8cf5d8def2972a3d5fe80c3e3a4eefb79db3f6984492b80ea48",
    ),
    (
        OrderedDict({3: 4, 1: 2}),
        b"cb2cb90289016eb180776fc056fa87d7037a0b91304817aa37b217187530c9ff",
    ),
    (
        range(1, 2, 3),
        b"8e19905aea3ca08a0edec0cc85a8e80eaae69193cb93136214c5f570a0021121",
    ),
    (
        slice(1, 2, 3),
        b"bf92450de58ece8b5525a1c442f882d94d5a9b0f1cbde7850510d0a74838cb01",
    ),
    # wonky types
    (
        sys,
        b"518b67e652531c5fe7e25d6b2c3b4ef6224e7d90da2091967dd47eb082b26a19",
    ),
    (
        list_in_self,
        b"e03f50c7b0624e5831ace9788342ec9d44cc68725cde30db6ac371adc470d1a3",
    ),
]


class ndarray:
    def tolist(self): ...


class Custom:
    def __shash__(self, enc: _SHash) -> bytes: ...


class TestShash(TestCase):
    def test_values(self):
        for value, expected in value2expected:
            with self.subTest(value=value, expected=expected):
                self.assertEqual(hex_hash(value), expected)

    def test_equivalence(self):
        self.assertEqual(b2a_hex(bin_hash(None)), hex_hash(None))

        self.assertEqual(hex_hash(set(range(100))), hex_hash(set(reversed(range(100)))))

        self.assertEqual(hex_hash({1: 2, 3: 4}), hex_hash({3: 4, 1: 2}))

    def test_difficulties(self):
        self.assertRaises(UnsupportedError, lambda: bin_hash(Unpickable()))

    def test_bad_unpickable(self):
        for probe in [
            object(),
            # from types
            len,
            [].append,
            object.__init__,
            object().__str__,
            str.join,
            # dict.__dict__["fromkeys"],
        ]:
            with self.subTest(probe=probe), self.assertWarns(UsesPickleWarning):
                bin_hash(probe)

    def test_locals(self):
        def make_closure():
            a = 1

            def func():
                return a  # pragma: no cover

            return func

        self.assertRaises(UsesLocalsError, lambda: bin_hash(make_closure()))

    def test_main(self):
        self.assertWarns(UsesMainWarning, lambda: bin_hash(fake_main_func))

    def test_numpy(self):
        numpy = Mock(spec=ModuleType)

        numpy.ndarray = ndarray
        numpy.dtype = Mock(spec=type)

        with patch.dict(sys.modules, numpy=numpy):
            del sys.modules["parao.shash"]

            from parao.shash import hex_hash

            nda = Mock(spec=ndarray)
            nda.tolist = Mock(return_value=[[[1], [2], [3]]])

            self.assertEqual(
                hex_hash(nda),
                b"6524a1a7d0e04156c52ae2000ba8081c769d66d381e06c06ec26fac508c7da75",
            )

            nda.tolist.assert_called_once()

    def test_custom(self):

        custom = Mock()
        custom.__shash__ = Mock()
        custom.__shash__.return_value = b"foobar"

        s = _SHash()

        self.assertEqual(s(custom), b"foobar")
        custom.__shash__.assert_called_once_with(s)
