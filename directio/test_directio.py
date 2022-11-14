#!/usr/bin/env python
# coding=utf-8

import os
import resource
import unittest

try:
    import directio
except ImportError:
    import sys
    sys.exit("""
    Please install directio:
      take a look at directio/README""")


alignment = resource.getpagesize()


class TestDirectio(unittest.TestCase):

    def setUp(self):
        super(TestDirectio, self).setUp()
        flags = os.O_RDWR | os.O_DIRECT | os.O_SYNC | os.O_CREAT | os.O_TRUNC
        self.filename = 'test.txt'
        self.fd = os.open(self.filename, flags, 0o666)
        self.buffer = bytearray(alignment)
        self.msg = b'It just works!'
        self.buffer[:len(self.msg)] = self.msg

    def tearDown(self):
        super(TestDirectio, self).tearDown()
        os.close(self.fd)
        os.unlink(self.filename)
        
    def test_read_after_write(self):
        # can write only immutable buffer, so we wrap buffer in bytes
        written = directio.write(self.fd, bytes(self.buffer))
        self.assertEqual(written, len(self.buffer))
        os.lseek(self.fd, 0, os.SEEK_SET)
        got = directio.read(self.fd, len(self.buffer))
        self.assertEqual(got, self.buffer)

    def test_fails_to_write_not_multiple_of_512(self):
        self.assertRaises(ValueError, directio.write, self.fd, self.msg)

    def test_fails_to_read_not_multiple_of_512(self):
        os.lseek(self.fd, 0, os.SEEK_SET)
        self.assertRaises(ValueError, directio.read, self.fd, 511)


if __name__ == '__main__':
    unittest.main()

