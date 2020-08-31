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

    def test_001_asset_provider(self):
        """Test asset providers API call."""
        provider = api.asset_provider(1)
        self.assertIsInstance(provider, pd.DataFrame, 'Response must be DataFrame')
        self.assertListEqual(provider.columns.to_list(), ['name'], 'DataFrame must have name column')
        self.assertRaises(TypeError, api.asset_provider, 'string')

    def test_002_asset_providers(self):
        providers = api.asset_providers()
        self.assertIsInstance(providers, pd.DataFrame, 'Response must be DataFrame')
        self.assertListEqual(providers.columns.to_list(), ['name'], 'DataFrame must have name column')

    def test_003_banks(self):
        """Test asset providers API call."""
        banks = api.banks()
        self.assertIsInstance(banks, pd.DataFrame, 'Response must be DataFrame')
        self.assertListEqual(banks.columns.to_list(), ['name'], 'DataFrame must have name column')

        banks = api.banks('de Chile')
        self.assertIsInstance(banks, pd.DataFrame, 'Response must be DataFrame')
        self.assertListEqual(banks.columns.to_list(), ['name'], 'DataFrame must have name column')

    def test_004_conceptual_asset(self):
        assets = api.conceptual_asset(16)
        columns = ['name', 'symbol', 'category', 'currency', 'max_scale', 'run', 'data_source']
        self.assertIsInstance(assets, pd.DataFrame, 'Response must be DataFrame')
        self.assertListEqual(assets.columns.to_list(), columns, 'Incorrect DataFrame columns')
        self.assertRaises(TypeError, api.conceptual_asset, 'string')

    def test_005_conceptual_assets(self):
        assets = api.conceptual_assets()
        columns = ['name', 'symbol', 'category', 'currency', 'max_scale', 'run', 'data_source']
        self.assertIsInstance(assets, pd.DataFrame, 'Response must be DataFrame')
        self.assertListEqual(assets.columns.to_list(), columns, 'Incorrect DataFrame columns')

    def test_006_real_asset(self):
        assets = api.real_asset(166)
        columns = ['name', 'symbol', 'serie', 'start_date', 'end_date',
                   'previous_asset_id', 'last_day_close_price', 'last_day_date']
        self.assertIsInstance(assets, pd.DataFrame, 'Response must be DataFrame')
        self.assertListEqual(assets.columns.to_list(), columns, 'Incorrect DataFrame columns')
        self.assertRaises(TypeError, api.real_asset, 'string')

    def test_007_real_assets(self):
        assets = api.real_assets(16)
        columns = ['name', 'symbol', 'serie', 'start_date', 'end_date',
                   'previous_asset_id', 'last_day_close_price', 'last_day_date']
        self.assertIsInstance(assets, pd.DataFrame, 'Response must be DataFrame')
        self.assertListEqual(assets.columns.to_list(), columns, 'Incorrect DataFrame columns')
        self.assertRaises(TypeError, api.real_assets, 'string')
