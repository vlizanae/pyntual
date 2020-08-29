import os
import requests
import pandas as pd


def _get_request(path: str, **kwargs: str) -> dict:
    url = os.path.join('https://fintual.cl/api', path)
    if kwargs:
        args = '&'.join([f'{key}={value}' for key, value in kwargs.items()])
        url = f'{url}?{args}'
    request = requests.get(url)
    request.raise_for_status()
    return request.json()['data']


def asset_providers(_id: int = None) -> pd.DataFrame:
    path = 'asset_providers'
    if _id:
        path = os.path.join(path, str(_id))
    data = _get_request(path)
    return pd.DataFrame([
        {'id': ap['id'], 'name': ap['attributes']['name']}
        for ap in data
    ]).sort_values('id').set_index('id').rename_axis(None)
