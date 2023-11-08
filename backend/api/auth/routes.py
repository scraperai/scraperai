import secrets
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.contrib.pydantic import pydantic_model_creator

from .models import User, Token
from .api_models import UserSignupRequestModel
from .google import oauth
from api.auth import yandex
from .cookies_oauth import OAuth2PasswordBearerWithCookie
from fastapi_admin.utils import hash_password, check_password

REDIRECT_URL_KEY = 'redirect-to'

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/token")
UserResponse = pydantic_model_creator(User, exclude=('password',))
TokenResponse = pydantic_model_creator(Token, exclude=('user', 'created'))

router = APIRouter()


async def auth_3rd_party(email: str, full_name: str, redirect_url: str) -> RedirectResponse:
    user = await User.get_or_none(email=email)
    if not user:
        user = await User.create(
            email=email,
            full_name=full_name,
            password=secrets.token_urlsafe(10)
        )
    token_obj = await Token.get_for_user(user)
    response = RedirectResponse(redirect_url)
    response.set_cookie(key="access_token", value=f"Bearer {token_obj.access_token}", httponly=True)
    return response


@router.post('/signup', response_model=UserResponse)
async def signup(user_in: UserSignupRequestModel):
    user = await User.create(
        email=user_in.email,
        full_name=user_in.full_name,
        password=hash_password(user_in.password)
    )
    return await UserResponse.from_tortoise_orm(user)


@router.post("/token")
async def auth(form_data: OAuth2PasswordRequestForm = Depends()):
    # if form_data.client_secret != settings.CLIENT_SECRET:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Incorrent client secret"
    #     )
    user = await User.get_or_none(email=form_data.username)
    if not user or not check_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token_obj = await Token.get_for_user(user)
    response = JSONResponse(content={'status': 'success'})
    response.set_cookie(key="access_token", value=f"Bearer {token_obj.access_token}", httponly=True)
    return response


@router.get('/auth/google')
async def auth_google(request: Request, redirect_url: str):
    # Redirect to Google for authentication
    # http://127.0.0.1:8000/api/auth/google?redirect_url=http://127.0.0.1:8000/api/users/me
    redirect_uri = request.url_for('auth_google_callback')
    request.session[REDIRECT_URL_KEY] = redirect_url
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/auth/google/callback')
async def auth_google_callback(request: Request):
    # Google callback route
    token = await oauth.google.authorize_access_token(request)
    email = token['userinfo']['email']
    full_name = token['userinfo'].get('name') or ''
    return await auth_3rd_party(email, full_name, redirect_url=request.session.get(REDIRECT_URL_KEY))


@router.get('/auth/yandex')
async def auth_yandex(request: Request, redirect_url: str):
    # http://127.0.0.1:8000/api/auth/yandex?redirect_url=http://127.0.0.1:8000/api/users/me

    redirect_uri = request.url_for('auth_yandex_callback')
    request.session[REDIRECT_URL_KEY] = redirect_url
    return RedirectResponse(yandex.get_oauth_url(redirect_uri))


@router.get('/auth/yandex/callback')
async def auth_yandex_callback(request: Request):
    code = request.query_params.get('code')
    token = yandex.get_token_by_code(code)
    email, full_name = yandex.get_user_info(token)
    return await auth_3rd_party(email, full_name, redirect_url=request.session.get(REDIRECT_URL_KEY))


@router.get("/users/me/", response_model=UserResponse, responses={404: {"model": HTTPNotFoundError}})
async def read_users_me(token: str = Depends(oauth2_scheme)):
    token_obj = await Token.get(access_token=token)
    user = token_obj.user
    return await UserResponse.from_queryset_single(user)
