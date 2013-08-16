#!/usr/bin/env python

__author__ = "Canine Mwenja"

from tests.fetchertest import FetcherTest

import unittest

if __name__ == "__main__": # run tests from command line
    suite = unittest.TestLoader().loadTestsFromTestCase(FetcherTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
