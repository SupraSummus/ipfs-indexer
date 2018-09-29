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
        self.assertIsNone(self.kv.get(b'aaa'))

    def test_set_get(self):
        self.set_get(b'aaa', b'bbb')

    def test_set_get_empty_key(self):
        self.set_get(b'', b'bbb')

    def test_set_get_strange_key(self):
        self.set_get(b'/"//..\0\t\n   \\', b'bbb')

    def test_update(self):
        self.kv.set(b'aaa', b'bbb')
        self.kv.set(b'aaa', b'ccc')
        self.assertEqual(self.kv.get(b'aaa'), b'ccc')
