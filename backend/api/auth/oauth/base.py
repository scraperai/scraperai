import datetime
from typing import Optional

from fastapi import HTTPException
from fastapi import Response
from fastapi import Security
from fastapi_jwt import JwtAccessCookie
from fastapi_jwt.jwt import JwtAuthBase, JwtAccess, JwtRefreshCookie, JwtRefresh
from starlette.status import HTTP_401_UNAUTHORIZED

from models.users import User


class JwtUserAccessCookie(JwtAccessCookie):
    def __init__(
        self,
        secret_key: str,
        auto_error: bool = True,
        access_expires_delta: Optional[datetime.timedelta] = None,
        refresh_expires_delta: Optional[datetime.timedelta] = None,
    ):
        super().__init__(
            secret_key=secret_key,
            auto_error=auto_error,
            access_expires_delta=access_expires_delta,
            refresh_expires_delta=refresh_expires_delta,
        )

    async def __call__(
            self,
            cookie: JwtAuthBase.JwtAccessCookie = Security(JwtAccess._cookie),
    ) -> Optional[User]:
        creds = await super().__call__(cookie)
        try:
            return await User.get(pk=creds.subject.get('pk'))
        except:
            if self.auto_error is None:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Wrong token: 'type' is not 'access'",
                )
            else:
                return None

    def create_and_set_tokens(self, response: Response, user_id: int):
        subject = {'pk': user_id}
        access_token = self.create_access_token(subject=subject)
        refresh_token = self.create_refresh_token(subject=subject)

        self.set_access_cookie(response, access_token)
        self.set_refresh_cookie(response, refresh_token)


class JwtUserRefreshCookie(JwtRefreshCookie):
    def __init__(
        self,
        secret_key: str,
        auto_error: bool = True,
        access_expires_delta: Optional[datetime.timedelta] = None,
        refresh_expires_delta: Optional[datetime.timedelta] = None,
    ):
        super().__init__(
            secret_key=secret_key,
            auto_error=auto_error,
            access_expires_delta=access_expires_delta,
            refresh_expires_delta=refresh_expires_delta,
        )

    async def __call__(
            self,
            cookie: JwtAuthBase.JwtRefreshCookie = Security(JwtRefresh._cookie),
    ) -> Optional[User]:
        creds = await super().__call__(cookie)
        try:
            return await User.get(pk=creds.subject.get('pk'))
        except:
            if self.auto_error is None:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Wrong token: 'type' is not 'refresh'",
                )
            else:
                return None
