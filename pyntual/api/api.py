import os
import requests
import pandas as pd

from requests import utils
from typing import Any, Type
from datetime import datetime


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

    # handling nested json (one level only)
    inner_json_columns = ['last_day']
    for column in dataframe.columns.to_list():
        if column in inner_json_columns:
            aux_df = pd.DataFrame.from_records(dataframe[column].to_list())
            aux_df = aux_df.rename(columns=lambda name: f'{column}_{name}')
            dataframe = dataframe.drop(columns=column).merge(aux_df, left_index=True, right_index=True)

    # type casting
    integer_columns = ['id', 'max_scale']
    float_columns = ['price', 'close_price', 'fixed_fee', 'variable_fee']
    float_columns += [f'last_day_{attr}' for attr in float_columns]
    date_columns = ['date', 'last_day_date']
    for column in dataframe.columns:
        if column in integer_columns:
            dataframe[column] = dataframe[column].astype(int)
        elif column in float_columns:
            dataframe[column] = pd.to_numeric(dataframe[column], errors='coerce')
        elif column in date_columns:
            dataframe[column] = pd.to_datetime(dataframe[column], errors='coerce')

    return dataframe.sort_values('id').set_index('id').rename_axis(None)


def _verify_type(variable: Any, _type: Type, name: str) -> None:
    if type(variable) != _type:
        raise TypeError(f'{name} ({variable}) must be {_type.__name__}, not {type(variable).__name__}.')


def _date_to_str(date: datetime) -> str:
    return date.strftime('%Y-%m-%d')


def asset_provider(_id: int) -> pd.DataFrame:
    _verify_type(_id, int, 'Asset provider id')
    path = os.path.join('asset_providers', str(_id))
    return _to_dataframe(_get_request(path))


def asset_providers() -> pd.DataFrame:
    return _to_dataframe(_get_request('asset_providers'))


def banks(query: str or None = None) -> pd.DataFrame:
    if query:
        data = _get_request('banks', q=query)
    else:
        data = _get_request('banks')
    return _to_dataframe(data)


def conceptual_asset(_id: int) -> pd.DataFrame:
    _verify_type(_id, int, 'Conceptual asset id')
    path = os.path.join('conceptual_assets', str(_id))
    return _to_dataframe(_get_request(path))


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


def real_asset(_id: int) -> pd.DataFrame:
    _verify_type(_id, int, 'Asset id')
    path = os.path.join('real_assets', str(_id))
    return _to_dataframe(_get_request(path))


def real_assets(conceptual_asset_id: int) -> pd.DataFrame:
    _verify_type(conceptual_asset_id, int, 'Conceptual asset id')
    path = os.path.join('conceptual_assets', str(conceptual_asset_id), 'real_assets')
    return _to_dataframe(_get_request(path))


def real_asset_days(_id: int,
                    date: datetime or None = None,
                    to_date: datetime or None = None,
                    from_date: datetime or None = None) -> pd.DataFrame:
    if date and (to_date or from_date):
        raise ValueError('Cannot set date along with to or from date.')
    path = os.path.join('real_assets', str(_id), 'days')

    if date:
        _verify_type(date, datetime, 'Date')
        data = _get_request(path, date=_date_to_str(date))
    elif to_date or from_date:
        params = {key: value for key, value in [('to_date', to_date), ('from_date', from_date)] if value}
        for key in params.keys():
            _verify_type(params[key], datetime, key)
            params[key] = _date_to_str(params[key])
        data = _get_request(path, **params)
    else:
        data = _get_request(path)

    return _to_dataframe(data)
