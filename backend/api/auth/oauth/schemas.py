import datetime

from fastapi_jwt import JwtAccessCookie

from .base import OAuthJWTSecurity
import settings


class OAuthSchemasBuilder:
    @staticmethod
    def build(auto_error: bool = True) -> OAuthJWTSecurity:
        return OAuthJWTSecurity(
            secret_key=settings.OAUTH_SECRET_KEY,
            auto_error=auto_error,
            access_expires_delta=datetime.timedelta(minutes=1),
            refresh_expires_delta=None
        )

