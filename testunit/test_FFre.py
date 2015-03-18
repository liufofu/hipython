from unittest import TestCase

__author__ = 'root'

from ffutil.ffre import FFre

class TestFFre(TestCase):
    def test_matchtest(self):
        fre=FFre()
        text = "JGood is a handsome boy, he is cool, clever, and so on..."
        fre.matchtest(text)
