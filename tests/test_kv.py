from unittest import TestCase
import ipfsapi
import io

from db import KV, Bytes


_client = ipfsapi.Client()
BYTES_A = Bytes(_client).set(b'AAAA')
BYTES_B = Bytes(_client).set(b'BBBB')
BYTES_C = Bytes(_client).set(b'CCCC')


class KVTestCase(TestCase):
    def setUp(self):
        self.kv = KV(Bytes)(backend=_client)

    def set_get(self, key, value):
        self.kv = self.kv.set(key, value)
        self.assertEqual(self.kv.get(key), value)

    def test_get_empty(self):
        self.assertEqual(self.kv.get(b'aaa'), None)

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

    def test_delete_by_setting_zero_value(self):
        self.assertEqual(
            self.kv.set(b'aaabbb', BYTES_A).set(b'aaabbb', Bytes(_client)),
            self.kv,
        )

    def test_keys_empty(self):
        self.assertEqual(list(self.kv.keys()), [])

    def test_keys_some(self):
        self.kv = self.kv.set(b'aaabbb', BYTES_A)
        self.kv = self.kv.set(b'aaa', BYTES_B)
        self.assertEqual(list(self.kv.keys()), [b'aaa', b'aaabbb'])

    def test_keys_start(self):
        self.kv = self.kv.set(b'aaa', BYTES_A)
        self.kv = self.kv.set(b'aab', BYTES_B)
        self.kv = self.kv.set(b'aabb', BYTES_C)
        self.assertEqual(list(self.kv.keys(b'aab')), [b'aab', b'aabb'])
