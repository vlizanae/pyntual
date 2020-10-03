import os
import requests
import pandas as pd

from requests import utils
from typing import Any, Type, Optional
from datetime import datetime


def _get_request(path: str, **kwargs: str) -> list:
    """
    Internal utility to wrap the logic of a GET request. It returns the raw JSON response as a list of dictionaries, if
    the response is a single dict, it is wrapped in a list. It raises an error if the response is not 200.

    :param path: URI of the request, not including base of the url nor GET parameters.
    :param kwargs: GET parameters (optional).
    :return: List of JSON response.
    """
    url = os.path.join('https://fintual.cl/api', path)
    if kwargs:
        args = '&'.join([f'{key}={value}' for key, value in kwargs.items()])
        url = utils.requote_uri(f'{url}?{args}')
    request = requests.get(url)
    request.raise_for_status()
    data = request.json()['data']
    return data if type(data) == list else [data]


def _to_dataframe(data: list) -> pd.DataFrame:
    """
    Internal utility to wrap the logic of turning an external API response into a dataframe using
    DataFrame.from_records constructor. It also handles JSON flattening and type casting.

    :param data: List of JSON data from external API.
    :return: Pandas DataFrame from data records.
    """
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
            # Apparently there are non integer ids. (?)
            try:
                dataframe[column] = dataframe[column].astype(int)
            except ValueError:
                pass
        elif column in float_columns:
            dataframe[column] = pd.to_numeric(dataframe[column], errors='coerce')
        elif column in date_columns:
            dataframe[column] = pd.to_datetime(dataframe[column], errors='coerce')

    return dataframe.sort_values('id').set_index('id').rename_axis(None)


def _verify_type(variable: Any, type_: Type, name: str) -> None:
    """
    Internal utility to assert proper input on the API calls. Raises TypeError.

    :param variable: Variable to be asserted.
    :param type_: Proper variable type.
    :param name: Name of the variable to be displayed on error message.
    """
    if type(variable) != type_:
        raise TypeError(f'{name} ({variable}) must be {type_.__name__}, not {type(variable).__name__}.')


def _date_to_str(date: datetime) -> str:
    """
    Internal utility that stores the correct text format for dates.

    :param date: Date to be converted.
    :return: Date as string with the format yyyy-mm-dd.
    """
    return date.strftime('%Y-%m-%d')


def asset_provider(id_: int) -> pd.DataFrame:
    """
    Corresponds to /asset_providers/{id} on external API.

    :param id_: parameter on external API.
    :return: Pandas DataFrame with the response data.
    """
    _verify_type(id_, int, 'Asset provider id')
    path = os.path.join('asset_providers', str(id_))
    return _to_dataframe(_get_request(path))


def asset_providers() -> pd.DataFrame:
    """
    Corresponds to /asset_providers on external API.

    :return: Pandas DataFrame with the response data.
    """
    return _to_dataframe(_get_request('asset_providers'))


def banks(query: Optional[str] = None) -> pd.DataFrame:
    """
    Corresponds to /banks on external API.

    :param query: parameter on external API.
    :return: Pandas DataFrame with the response data.
    """
    if query:
        data = _get_request('banks', q=query)
    else:
        data = _get_request('banks')
    return _to_dataframe(data)


def conceptual_asset(id_: int) -> pd.DataFrame:
    """
    Corresponds to /conceptual_assets/{id} on external API.

    :param id_: parameter on external API.
    :return: Pandas DataFrame with the response data.
    """
    _verify_type(id_, int, 'Conceptual asset id')
    path = os.path.join('conceptual_assets', str(id_))
    return _to_dataframe(_get_request(path))


def conceptual_assets(asset_provider_id: Optional[int] = None,
                      run: Optional[str] = None,
                      name: Optional[str] = None) -> pd.DataFrame:
    """
    Corresponds to /conceptual_assets and /asset_providers/{asset_provider_id}/conceptual_assets on external API.

    :param asset_provider_id: parameter on external API.
    :param run: parameter on external API.
    :param name: parameter on external API.
    :return: Pandas DataFrame with the response data.
    """
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


def real_asset(id_: int) -> pd.DataFrame:
    """
    Corresponds to /real_assets/{id} on external API.

    :param id_: parameter on external API.
    :return: Pandas DataFrame with the response data.
    """
    _verify_type(id_, int, 'Asset id')
    path = os.path.join('real_assets', str(id_))
    return _to_dataframe(_get_request(path))


def real_assets(conceptual_asset_id: int) -> pd.DataFrame:
    """
    Corresponds to /conceptual_assets/{conceptual_asset_id}/real_assets on external API.

    :param conceptual_asset_id: parameter on external API.
    :return: Pandas DataFrame with the response data.
    """
    _verify_type(conceptual_asset_id, int, 'Conceptual asset id')
    path = os.path.join('conceptual_assets', str(conceptual_asset_id), 'real_assets')
    return _to_dataframe(_get_request(path))


def real_asset_days(id_: int,
                    date: Optional[datetime] = None,
                    to_date: Optional[datetime] = None,
                    from_date: Optional[datetime] = None) -> pd.DataFrame:
    """
    Corresponds to /real_assets/{real_asset_id}/days on external API.

    :param id_: parameter on external API.
    :param date: parameter on external API. If set, to_date and from_date must be absent.
    :param to_date: parameter on external API. If set, date must be absent.
    :param from_date: parameter on external API. If set, date must be absent.
    :return: Pandas DataFrame with the response data.
    """
    _verify_type(id_, int, 'Real asset id')
    if date and (to_date or from_date):
        raise ValueError('Cannot set date along with to or from date.')
    path = os.path.join('real_assets', str(id_), 'days')

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
