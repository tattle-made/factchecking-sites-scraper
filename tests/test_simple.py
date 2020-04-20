import unittest

class TestTrial(unittest.TestCase):
    def test_one(self):
        self.assertEqual("tattle".upper(), "TATTLE")