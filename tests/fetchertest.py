#!/usr/bin/env python

__author__ = "Canine Mwenja"

import lib.fetcher
import unittest

class FetcherTest(unittest.TestCase):
	""" testing for success of Fetcher functions """

	def setUp(self):
		self.fetcher = lib.fetcher.Fetcher()

	def test_get_full_url(self):
		control_data = "https://api.github.com/helloworld"
		self.assertEqual(control_data, self.fetcher.get_full_url("helloworld"))

	def tearDown(self):
		self.fetcher = None

if __name__ == "__main__":
	unittest.main()
