from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

import settings

config_data = {
    'GOOGLE_CLIENT_ID': settings.GOOGLE_CLIENT_ID,
    'GOOGLE_CLIENT_SECRET': settings.GOOGLE_CLIENT_SECRET
}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
    authorize_state=settings.SECRET_KEY
)
