import os
import requests
import pandas as pd

from requests import utils
from typing import Any, Type


def _get_request(path: str, **kwargs: str) -> dict:
    url = os.path.join('https://fintual.cl/api', path)
    if kwargs:
        args = '&'.join([f'{key}={value}' for key, value in kwargs.items()])
        url = utils.requote_uri(f'{url}?{args}')
    request = requests.get(url)
    request.raise_for_status()
    data = request.json()['data']
    return data if type(data) == list else [data]


def _to_dataframe(data: list) -> pd.DataFrame:
    if len(data) == 0:
        return pd.DataFrame()
    dataframe = pd.DataFrame.from_records(map(lambda item: {'id': item['id'], **item['attributes']}, data))
    dataframe['id'] = dataframe['id'].astype(int)
    return dataframe.sort_values('id').set_index('id').rename_axis(None)


def _verify_type(variable: Any, _type: Type, name: str) -> None:
    if type(variable) != _type:
        raise TypeError(f'{name} ({variable}) must be {_type.__name__}, not {type(variable).__name__}.')


def asset_providers() -> pd.DataFrame:
    return _to_dataframe(_get_request('asset_providers'))


def asset_provider(_id: int) -> pd.DataFrame:
    _verify_type(_id, int, 'Asset provider id')
    path = os.path.join('asset_providers', str(_id))
    return _to_dataframe(_get_request(path))


def banks(query: str or None = None) -> pd.DataFrame:
    if query:
        data = _get_request('banks', q=query)
    else:
        data = _get_request('banks')
    return _to_dataframe(data)


def conceptual_assets(asset_provider_id: int or None = None,
                      run: str or None = None,
                      name: str or None = None) -> pd.DataFrame:
    path = 'conceptual_assets'
    if asset_provider_id:
        _verify_type(asset_provider_id, int, 'Asset provider id')
        path = os.path.join('asset_providers', str(asset_provider_id), path)

    if run or name:
        params = {key: value for key, value in [('run', run), ('name', name)] if value}
        data = _get_request(path, **params)
    else:
        data = _get_request(path)
    return _to_dataframe(data)


def conceptual_asset(_id: int) -> pd.DataFrame:
    _verify_type(_id, int, 'Conceptual asset id')
    path = os.path.join('conceptual_assets', str(_id))
    return _to_dataframe(_get_request(path))
