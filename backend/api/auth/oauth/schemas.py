import datetime

from .base import JwtUserAccessCookie, JwtUserRefreshCookie
import settings


access_expires_delta = datetime.timedelta(hours=1)
refresh_expires_delta = None


class OAuthSchemasBuilder:
    @staticmethod
    def build(auto_error: bool = True) -> JwtUserAccessCookie:
        return JwtUserAccessCookie(
            secret_key=settings.OAUTH_SECRET_KEY,
            auto_error=auto_error,
            access_expires_delta=access_expires_delta,
            refresh_expires_delta=refresh_expires_delta
        )

    @staticmethod
    def build_refresh_schema() -> JwtUserRefreshCookie:
        return JwtUserRefreshCookie(
            secret_key=settings.OAUTH_SECRET_KEY,
            auto_error=True,
            access_expires_delta=access_expires_delta,
            refresh_expires_delta=refresh_expires_delta
        )
