import os

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from fastapi_admin.exceptions import (
    forbidden_error_exception,
    not_found_error_exception,
    server_error_exception,
    unauthorized_error_exception,
)

from models.users import User
from settings import REDIS_URL, BASE_DIR
from .routes import router
from .resources import (UserResource, GithubLink, DocumentationLink)
from .providers import LoginProvider


def register(app: FastAPI):
    admin_app.add_exception_handler(HTTP_500_INTERNAL_SERVER_ERROR, server_error_exception)
    admin_app.add_exception_handler(HTTP_404_NOT_FOUND, not_found_error_exception)
    admin_app.add_exception_handler(HTTP_403_FORBIDDEN, forbidden_error_exception)
    admin_app.add_exception_handler(HTTP_401_UNAUTHORIZED, unauthorized_error_exception)
    admin_app.include_router(router)
    app.mount("/admin", admin_app)


async def on_startup():
    r = redis.from_url(
        REDIS_URL,
        decode_responses=True,
        encoding="utf8",
    )
    await admin_app.configure(
        admin_path="/admin",
        logo_url="/static/logo.png",
        favicon_url="https://raw.githubusercontent.com/fastapi-admin/fastapi-admin/dev/images/favicon.png",
        template_folders=[os.path.join(BASE_DIR, "templates")],
        providers=[
            LoginProvider(
                login_logo_url="/static/logo.png",
                admin_model=User,
            )
        ],
        default_locale='en_US',
        language_switch=False,
        redis=r,
    )
