import base64

import httpx
from starlette.datastructures import URL

import settings


def get_oauth_url(redirect_uri: URL) -> str:
    return f'https://oauth.yandex.ru/authorize?' \
           f'response_type=code' \
           f'&client_id={settings.YANDEX_CLIENT_ID}' \
           f'&redirect_uri={redirect_uri}'


async def get_token_by_code(code: str) -> str:
    url = 'https://oauth.yandex.ru/token'
    data = {
        'code': code,
        'grant_type': 'authorization_code',
        'client_id': settings.YANDEX_CLIENT_ID
    }
    y_token = f'{settings.YANDEX_CLIENT_ID}:{settings.YANDEX_CLIENT_SECRET}'
    y_token = base64.b64encode(y_token.encode()).decode()

    headers = {
        'Authorization': f'Basic {y_token}'
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data, headers=headers)
        response = response.json()
    return response['access_token']


async def get_user_info(token: str) -> tuple[str, str]:
    """
    Fetches Yandex's user' info
    :return: tuple of (email, full_name)
    """
    url = 'https://login.yandex.ru/info'
    headers = {
        'Authorization': f'OAuth {token}'
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params={'format': 'json'}, headers=headers)
        response = response.json()
    return response['default_email'], response['real_name']
