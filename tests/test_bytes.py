from unittest import TestCase
import ipfsapi

from db import Bytes


class BytesTestCase(TestCase):
    def setUp(self):
        self.bytes = Bytes(ipfsapi.Client())

    def test_empty(self):
        self.assertEqual(self.bytes.value, b'')

    def test_set(self):
        self.bytes = self.bytes.set(b'You suck at cooking')
        self.assertEqual(self.bytes.value, b'You suck at cooking')
