#!/usr/bin/env python

__author__ = "Canine Mwenja"

import lib.fetcher
import unittest
import os

from mock import Mock

class FetcherTest(unittest.TestCase):
	""" testing for success of Fetcher functions """

	def get_data_file(self, filename):
		""" returns the content of a test data file in ./data"""
		test_data = os.path.join(os.path.dirname(__file__), "data")
		f = open(os.path.join(test_data,filename))
		data = f.read()
		f.close()
		return data

	def setUp(self):
		self.fetcher = lib.fetcher.Fetcher()

	def test_get_full_url(self):
		control_data = "https://api.github.com/helloworld"
		self.assertEqual(control_data, self.fetcher.get_full_url("helloworld"))

	def test_process_repo_single_repo(self):
		self.fetcher.get_from_net = Mock(return_value=self.get_data_file("octocat.Spoon-Knife.json"))
		result = self.fetcher.process_repo("")
		self.assertIsInstance(result, type(list()), "Result was not a list")
		self.assertNotEqual(len(result), 0, "List is empty")
		self.assertEqual(len(result), 1, "List has extra items")

	def tearDown(self):
		self.fetcher = None

if __name__ == "__main__":
	unittest.main()
