from unittest import TestCase
import ipfsapi
import io

from db.kv import KV


_client = ipfsapi.Client()
HASH_A = _client.object_put(io.BytesIO(b'{"Data": "AAAA", "Links": []}'))['Hash']
HASH_B = _client.object_put(io.BytesIO(b'{"Data": "BBBB", "Links": []}'))['Hash']
HASH_C = _client.object_put(io.BytesIO(b'{"Data": "CCCC", "Links": []}'))['Hash']


class KVTestCase(TestCase):
    def setUp(self):
        self.kv = KV(ipfs_api=ipfsapi.Client())

    def set_get(self, key, value):
        self.kv.set(key, value)
        self.assertEqual(self.kv.get(key), value)

    def test_get_empty(self):
        self.assertEqual(self.kv.get(b'aaa'), None)

    def test_set_get(self):
        self.set_get(b'aaa', HASH_A)

    def test_set_get_empty_key(self):
        self.set_get(b'', HASH_A)

    def test_set_get_strange_key(self):
        self.set_get(b'/"//..\0\t\n   \\', HASH_A)

    def test_set_get_on_path(self):
        self.kv.set(b'aaa', HASH_A)
        self.set_get(b'aa', HASH_B)
        self.assertEqual(self.kv.get(b'aaa'), HASH_A)

    def test_update(self):
        self.kv.set(b'aaa', HASH_A)
        self.kv.set(b'aaa', HASH_B)
        self.assertEqual(self.kv.get(b'aaa'), HASH_B)

    def test_delete(self):
        empty_hash = self.kv.state_hash
        self.kv.set(b'aaabbb', HASH_A)
        self.kv.set(b'aaabbb', None)
        self.assertEqual(self.kv.state_hash, empty_hash)

    def test_keys_empty(self):
        self.assertEqual(list(self.kv.keys()), [])

    def test_keys_some(self):
        self.kv.set(b'aaabbb', HASH_A)
        self.kv.set(b'aaa', HASH_B)
        self.assertEqual(list(self.kv.keys()), [b'aaa', b'aaabbb'])

    def test_keys_start(self):
        self.kv.set(b'aaa', HASH_A)
        self.kv.set(b'aab', HASH_B)
        self.kv.set(b'aabb', HASH_C)
        self.assertEqual(list(self.kv.keys(b'aab')), [b'aab', b'aabb'])
