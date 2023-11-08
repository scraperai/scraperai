import secrets
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from starlette import status

from api.api_models import SuccessResponse
from api.auth.models import User, Token
from api.auth.api_models import UserSignupForm, PasswordChangeForm, PasswordResetResponse
from api.auth.google import oauth
from api.auth import yandex
from api.auth.cookies_oauth import OAuth2PasswordBearerWithCookie
from fastapi_admin.utils import hash_password, check_password

from api.auth.utils import send_email

REDIRECT_URL_KEY = 'redirect-to'

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/auth")
UserResponse = User.get_pydantic()
TokenResponse = Token.get_pydantic()

router = APIRouter(tags=['Auth'], prefix='/auth')


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
async def signup(user_in: UserSignupForm):
    user = await User.create(
        email=user_in.email,
        full_name=user_in.full_name,
        password=hash_password(user_in.password)
    )
    return await UserResponse.from_tortoise_orm(user)


@router.post("/")
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


@router.post('/change-password')
async def change_password(form: PasswordChangeForm, token: str = Depends(oauth2_scheme)):
    user = await User.from_token(token)
    if not check_password(form.current_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    if form.new_password != form.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match",
        )
    if form.new_password == form.current_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the old one"
        )
    user.password = hash_password(form.new_password)
    await user.save()
    return SuccessResponse()


@router.post("/password-recovery")
async def send_password_recovery(email: EmailStr, background_tasks: BackgroundTasks):
    user = await User.get_or_none(email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email",
        )
    verification_code = secrets.token_urlsafe(6)
    user.verification_code = verification_code
    await user.save()

    subject = "Password Recovery Instructions"
    body = f"Please use the following code to reset your password: {verification_code}"
    print(subject)
    print(body)
    print('--------')
    await send_email(email, subject, body)

    # Send the email in the background
    background_tasks.add_task(send_email, email=email, subject=subject, body=body)
    return SuccessResponse()


@router.post("/password-reset", response_model=PasswordResetResponse)
async def reset_password(email: EmailStr, verification_code: str):
    user = await User.get_or_none(email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email",
        )
    if verification_code != user.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong code",
        )
    new_password = secrets.token_urlsafe(8)
    user.password = hash_password(new_password)
    user.verification_code = None
    await user.save()

    token_obj = await Token.get_for_user(user)

    response = PasswordResetResponse(new_password=new_password)
    response = JSONResponse(content=jsonable_encoder(response))
    response.set_cookie(key="access_token", value=f"Bearer {token_obj.access_token}", httponly=True)
    return response


@router.get('/google')
async def auth_google(request: Request, redirect_url: str):
    # Redirect to Google for authentication
    # http://127.0.0.1:8000/api/auth/google?redirect_url=http://127.0.0.1:8000/api/users/me
    redirect_uri = request.url_for('auth_google_callback')
    request.session[REDIRECT_URL_KEY] = redirect_url
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/google/callback', include_in_schema=False)
async def auth_google_callback(request: Request):
    # Google callback route
    token = await oauth.google.authorize_access_token(request)
    email = token['userinfo']['email']
    full_name = token['userinfo'].get('name') or ''
    return await auth_3rd_party(email, full_name, redirect_url=request.session.get(REDIRECT_URL_KEY))


@router.get('/yandex')
async def auth_yandex(request: Request, redirect_url: str):
    # http://127.0.0.1:8000/api/auth/yandex?redirect_url=http://127.0.0.1:8000/api/users/me

    redirect_uri = request.url_for('auth_yandex_callback')
    request.session[REDIRECT_URL_KEY] = redirect_url
    return RedirectResponse(yandex.get_oauth_url(redirect_uri))


@router.get('/yandex/callback', include_in_schema=False)
async def auth_yandex_callback(request: Request):
    code = request.query_params.get('code')
    token = yandex.get_token_by_code(code)
    email, full_name = yandex.get_user_info(token)
    return await auth_3rd_party(email, full_name, redirect_url=request.session.get(REDIRECT_URL_KEY))
