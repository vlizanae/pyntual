#!/usr/bin/env python

"""Tests for `pyntual` package."""


import unittest
import pandas as pd

from pyntual import api


class TestPyntualAPI(unittest.TestCase):
    """Tests for `pyntual` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        pass

    def tearDown(self):
        """Tear down test fixtures, if any."""
        pass

    def test_001_asset_providers(self):
        """Test asset providers API call."""
        providers = api.asset_providers(1)
        self.assertIsInstance(providers, pd.DataFrame, 'Response must be DataFrame')
        self.assertListEqual(providers.columns.to_list(), ['name'], 'DataFrame must have name column')
