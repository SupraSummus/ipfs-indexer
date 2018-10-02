from unittest import TestCase

import ipfsapi

from db import Bytes, Record


_client = ipfsapi.Client()
BYTES_A = Bytes(_client).set(b'AAAA')


class RecordTestCase(TestCase):
    def test_get_empty(self):
        self.assertEqual(
            Record({'aaa': Bytes})(_client).get('aaa'),
            Bytes(_client),
        )

    def test_get_nonexistent_field(self):
        with self.assertRaises(Exception):
            Record({})(_client).get('aaa')

    def test_set_nonexistent_field(self):
        with self.assertRaises(Exception):
            Record({})(_client).set('aaa', BYTES_A)
        
    def test_set_get(self):
        self.assertEqual(
            Record({'aaa': Bytes})(_client).set('aaa', BYTES_A).get('aaa'),
            BYTES_A,
        )
