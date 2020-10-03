#!/usr/bin/env python

"""Tests for `pyntual` package."""

import json
import os
import pandas as pd
import unittest

from datetime import datetime
from requests import Response
from requests.exceptions import HTTPError
from typing import Optional, List, Callable
from unittest.mock import patch

from pyntual import api


class TestPyntualAPI(unittest.TestCase):
    """Tests for `pyntual.api` package."""
    ASSET_PROVIDER_COLUMNS = ['name']
    CONCEPTUAL_ASSET_COLUMNS = ['name', 'symbol', 'category', 'currency', 'max_scale', 'run', 'data_source']
    REAL_ASSET_COLUMNS = ['name', 'symbol', 'serie', 'start_date', 'end_date',
                          'previous_asset_id', 'last_day_close_price', 'last_day_date']
    REAL_ASSET_DAY_COLUMNS = ['date', 'price', 'close_price', 'close_price_type']

    def json_response_dataframe_test(self,
                                     json_response: str,
                                     api_call: Callable[..., pd.DataFrame],
                                     *args,
                                     columns: Optional[List[str]] = None,
                                     **kwargs) -> None:
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            dirname = os.path.dirname(__file__)
            with open(os.path.join(dirname, 'json_responses', f'{json_response}.json')) as json_response_file:
                mock_get.return_value.json.return_value = json.load(json_response_file)
            dataframe = api_call(*args, **kwargs)
        self.assertIsInstance(dataframe, pd.DataFrame, 'Response must be DataFrame')
        if columns:
            self.assertListEqual(dataframe.columns.to_list(), columns, 'Incorrect DataFrame columns')

    def not_found_test(self, api_call: Callable[..., pd.DataFrame], *args, **kwargs) -> None:
        with patch('requests.get') as mock_get:
            mock_get.return_value = Response()
            mock_get.return_value.status_code = 404
            self.assertRaises(HTTPError, api_call, *args, **kwargs)

    def test_001_asset_provider(self):
        self.json_response_dataframe_test('asset_provider_3', api.asset_provider, 3,
                                          columns=self.ASSET_PROVIDER_COLUMNS)

    def test_002_asset_provider_wrong_type(self):
        self.assertRaises(TypeError, api.asset_provider, 'string')

    def test_003_asset_provider_not_found(self):
        self.not_found_test(api.asset_provider, 1)

    def test_004_asset_providers(self):
        self.json_response_dataframe_test('asset_providers', api.asset_providers, columns=self.ASSET_PROVIDER_COLUMNS)

    def test_005_banks(self):
        self.json_response_dataframe_test('banks', api.banks, columns=self.ASSET_PROVIDER_COLUMNS)

    def test_006_banks_query(self):
        self.json_response_dataframe_test('banks_q_de_chile', api.banks, 'de chile',
                                          columns=self.ASSET_PROVIDER_COLUMNS)

    def test_007_banks_query_empty(self):
        self.json_response_dataframe_test('empty_data', api.banks, 'empty')

    def test_008_conceptual_asset(self):
        self.json_response_dataframe_test('conceptual_asset_25', api.conceptual_asset, 25,
                                          columns=self.CONCEPTUAL_ASSET_COLUMNS)

    def test_009_conceptual_asset_wrong_type(self):
        self.assertRaises(TypeError, api.conceptual_asset, 'string')

    def test_010_conceptual_asset_not_found(self):
        self.not_found_test(api.conceptual_asset, 1)

    def test_011_conceptual_assets(self):
        self.json_response_dataframe_test('conceptual_assets', api.conceptual_assets,
                                          columns=self.CONCEPTUAL_ASSET_COLUMNS)

    def test_012_conceptual_assets_id(self):
        self.json_response_dataframe_test('conceptual_assets_3', api.conceptual_assets, asset_provider_id=3,
                                          columns=self.CONCEPTUAL_ASSET_COLUMNS)

    def test_013_conceptual_assets_name(self):
        self.json_response_dataframe_test('conceptual_assets_name_chile', api.conceptual_assets, name='chile',
                                          columns=self.CONCEPTUAL_ASSET_COLUMNS)

    def test_014_conceptual_assets_full(self):
        self.json_response_dataframe_test('conceptual_assets_name_chile', api.conceptual_assets, asset_provider_id=3,
                                          name='chile', run='9854-k', columns=self.CONCEPTUAL_ASSET_COLUMNS)

    def test_015_conceptual_assets_empty(self):
        self.json_response_dataframe_test('empty_data', api.conceptual_assets, name='empty', run='1234-5')

    def test_016_conceptual_assets_not_found(self):
        self.not_found_test(api.conceptual_assets, 1)

    def test_017_real_asset(self):
        self.json_response_dataframe_test('real_asset_166', api.real_asset, 166, columns=self.REAL_ASSET_COLUMNS)

    def test_018_real_asset_wrong_type(self):
        self.assertRaises(TypeError, api.real_asset, 'string')

    def test_019_real_asset_not_found(self):
        self.not_found_test(api.real_asset, 1)

    def test_020_real_assets(self):
        self.json_response_dataframe_test('real_assets_25', api.real_assets, 25, columns=self.REAL_ASSET_COLUMNS)

    def test_021_real_assets_wrong_type(self):
        self.assertRaises(TypeError, api.real_assets, 'string')

    def test_022_real_assets_empty(self):
        self.json_response_dataframe_test('empty_data', api.real_assets, 1)

    def test_023_real_asset_days(self):
        self.json_response_dataframe_test('real_asset_days_166', api.real_asset_days, 166,
                                          columns=self.REAL_ASSET_DAY_COLUMNS)

    def test_024_real_asset_days_wrong_params(self):
        self.assertRaises(ValueError, api.real_asset_days, 166, date=datetime.now(), from_date=datetime.now())

    def test_025_real_asset_days_empty(self):
        self.json_response_dataframe_test('empty_data', api.real_asset_days, 166, date=datetime.fromtimestamp(0))

    def test_026_real_asset_days_date(self):
        self.json_response_dataframe_test('real_asset_days_166_20200922', api.real_asset_days, 166,
                                          date=datetime(2020, 9, 22), columns=self.REAL_ASSET_DAY_COLUMNS)

    def test_027_real_asset_days_to_from_date(self):
        self.json_response_dataframe_test('real_asset_days_166_20200922_25', api.real_asset_days, 166,
                                          from_date=datetime(2020, 9, 22), to_date=datetime(2020, 9, 22),
                                          columns=self.REAL_ASSET_DAY_COLUMNS)

    def test_028_real_asset_days_wrong_types(self):
        self.assertRaises(TypeError, api.real_asset_days, 'string')
        self.assertRaises(TypeError, api.real_asset_days, 166, date='string')
        self.assertRaises(TypeError, api.real_asset_days, 166, from_date='string')
        self.assertRaises(TypeError, api.real_asset_days, 166, to_date='string')

    def test_029_real_asset_days_not_found(self):
        self.not_found_test(api.real_asset_days, 1)
