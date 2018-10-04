from unittest import TestCase
import ipfsapi

from db import KV, Bytes


_client = ipfsapi.Client()
BYTES_A = Bytes(_client).set(b'AAAA')
BYTES_B = Bytes(_client).set(b'BBBB')
BYTES_C = Bytes(_client).set(b'CCCC')
BYTES_ZERO = Bytes(_client)


class KVTestCase(TestCase):
    def setUp(self):
        self.kv = KV(Bytes)(backend=_client)

    def set_get(self, key, value):
        self.kv = self.kv.set(key, value)
        self.assertEqual(self.kv.get(key), value)

    def test_get_empty(self):
        self.assertEqual(self.kv.get(b'aaa'), BYTES_ZERO)

    def test_set_empty_makes_no_difference(self):
        self.assertEqual(
            self.kv.set(b'bbb', BYTES_A),
            self.kv.set(b'bbb', BYTES_A).set(b'bba', BYTES_ZERO),
        )

    def test_set_get(self):
        self.set_get(b'aaa', BYTES_A)

    def test_set_get_empty_key(self):
        self.set_get(b'', BYTES_A)

    def test_set_get_strange_key(self):
        self.set_get(b'/"//..\0\t\n   \\', BYTES_A)

    def test_set_get_on_path(self):
        self.kv = self.kv.set(b'aaa', BYTES_A)
        self.set_get(b'aa', BYTES_B)
        self.assertEqual(self.kv.get(b'aaa'), BYTES_A)

    def test_update(self):
        self.kv = self.kv.set(b'aaa', BYTES_A)
        self.kv = self.kv.set(b'aaa', BYTES_B)
        self.assertEqual(self.kv.get(b'aaa'), BYTES_B)

    def test_delete(self):
        self.assertEqual(
            self.kv.set(b'aaabbb', BYTES_A)
                   .set(b'aaabbb', BYTES_ZERO),
            self.kv,
        )

    def test_delete_nested(self):
        self.assertEqual(
            self.kv.set(b'aaa', BYTES_A)
                   .set(b'aaaa', BYTES_B)
                   .set(b'aaa', BYTES_ZERO),
            self.kv.set(b'aaaa', BYTES_B),
        )

    def test_delete_nested_2(self):
        self.assertEqual(
            self.kv.set(b'aaaa', BYTES_A)
                   .set(b'aaa', BYTES_B)
                   .set(b'aaaa', BYTES_ZERO),
            self.kv.set(b'aaa', BYTES_B),
        )

    def test_entries_empty(self):
        self.assertEqual(list(self.kv.entries()), [])

    def test_entries_some(self):
        self.kv = self.kv.set(b'aaabbb', BYTES_A)
        self.kv = self.kv.set(b'aaa', BYTES_B)
        self.assertEqual(
            list(self.kv.entries()),
            [(b'aaa', BYTES_B), (b'aaabbb', BYTES_A)],
        )

    def test_entries_start(self):
        self.kv = self.kv.set(b'aaa', BYTES_A)
        self.kv = self.kv.set(b'aab', BYTES_B)
        self.kv = self.kv.set(b'aabb', BYTES_C)
        self.assertEqual(
            list(self.kv.entries(b'aab')),
            [(b'aab', BYTES_B), (b'aabb', BYTES_C)],
        )

    def test_dump(self):
        self.assertEqual(
            self.kv.set(b'abcd', BYTES_A)
                   .set(b'bcd', BYTES_B)
                   .set(b'abce', BYTES_C)
                   .set(b'abced', BYTES_B)
                   .dump,
            {
                b'abc': {
                    b'd': BYTES_A.state_hash,
                    b'e': {
                        b'': BYTES_C.state_hash,
                        b'd': BYTES_B.state_hash,
                    },
                },
                b'bcd': BYTES_B.state_hash,
            },
        )
