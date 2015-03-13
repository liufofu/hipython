from unittest import TestCase

__author__ = 'liufofu'

from ffutil.global_func import mkrndpasswd

class TestGlobalFunc(TestCase):
    def test_mkrndpasswd(self):
        print mkrndpasswd(rlen=1)