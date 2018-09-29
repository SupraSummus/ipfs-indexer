from unittest import TestCase
import ipfsapi

from db.kv import KV


class KVTestCase(TestCase):
    def setUp(self):
        self.kv = KV(ipfs_api=ipfsapi.Client())

    def set_get(self, key, value):
        self.kv.set(key, value)
        self.assertEqual(self.kv.get(key), value)

    def test_get_empty(self):
        self.assertEqual(self.kv.get(b'aaa'), b'')

    def test_set_get(self):
        self.set_get(b'aaa', b'bbb')

    def test_set_get_empty_key(self):
        self.set_get(b'', b'bbb')

    def test_set_get_strange_key(self):
        self.set_get(b'/"//..\0\t\n   \\', b'bbb')

    def test_set_get_on_path(self):
        self.kv.set(b'aaa', b'bbb')
        self.set_get(b'aa', b'ccc')
        self.assertEqual(self.kv.get(b'aaa'), b'bbb')

    def test_update(self):
        self.kv.set(b'aaa', b'bbb')
        self.kv.set(b'aaa', b'ccc')
        self.assertEqual(self.kv.get(b'aaa'), b'ccc')

    def test_delete(self):
        empty_hash = self.kv.state_hash
        self.kv.set(b'aaabbb', b'ccc')
        self.kv.set(b'aaabbb', b'')
        self.assertEqual(self.kv.state_hash, empty_hash)

    def test_keys_empty(self):
        self.assertEqual(list(self.kv.keys()), [])

    def test_keys_some(self):
        self.kv.set(b'aaabbb', b'ccc')
        self.kv.set(b'aaa', b'ddd')
        self.assertEqual(list(self.kv.keys()), [b'aaa', b'aaabbb'])

    def test_keys_start(self):
        self.kv.set(b'aaa', b'ddd')
        self.kv.set(b'aab', b'ddd')
        self.kv.set(b'aabb', b'ddd')
        self.assertEqual(list(self.kv.keys(b'aab')), [b'aab', b'aabb'])
