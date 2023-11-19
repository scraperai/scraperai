import uuid

from aioredis import Redis
from fastapi import Depends
from fastapi_admin import constants
from fastapi_admin.template import templates
from fastapi_admin.utils import check_password
from starlette.requests import Request

from fastapi_admin.depends import get_redis
from fastapi_admin.providers.login import UsernamePasswordProvider
from starlette.responses import RedirectResponse
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_303_SEE_OTHER, HTTP_403_FORBIDDEN
from fastapi_admin.i18n import _

from models.users import User


class LoginProvider(UsernamePasswordProvider):
    async def login(self, request: Request, redis: Redis = Depends(get_redis)):
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        remember_me = form.get("remember_me")
        admin = await User.get_or_none(username=username)
        if not admin or not check_password(password, admin.password):
            return templates.TemplateResponse(
                self.template,
                status_code=HTTP_401_UNAUTHORIZED,
                context={"request": request, "error": _("login_failed")},
            )
        if 'admin' not in await admin.roles_set:
            return templates.TemplateResponse(
                self.template,
                status_code=HTTP_403_FORBIDDEN,
                context={"request": request, "error": _("login_failed")},
            )
        response = RedirectResponse(url=request.app.admin_path, status_code=HTTP_303_SEE_OTHER)
        if remember_me == "on":
            expire = 3600 * 24 * 30
            response.set_cookie("remember_me", "on")
        else:
            expire = 3600
            response.delete_cookie("remember_me")
        token = uuid.uuid4().hex
        response.set_cookie(
            self.access_token,
            token,
            expires=expire,
            path=request.app.admin_path,
            httponly=True,
        )
        await redis.set(constants.LOGIN_USER.format(token=token), admin.pk, ex=expire)
        return response
