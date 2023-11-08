import datetime

from fastapi import APIRouter, HTTPException, Depends
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.contrib.pydantic import pydantic_model_creator

from .models import User, Token
from .api_models import UserSignupRequestModel
from fastapi_admin.utils import hash_password, check_password
import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")
UserResponse = pydantic_model_creator(User, exclude=('password',))
TokenResponse = pydantic_model_creator(Token, exclude=('user', 'created'))

router = APIRouter()


@router.post('/signup', response_model=UserResponse)
async def signup(user_in: UserSignupRequestModel):
    user = await User.create(
        email=user_in.email,
        full_name=user_in.full_name,
        password=hash_password(user_in.password)
    )
    return await UserResponse.from_tortoise_orm(user)


@router.post("/token", response_model=TokenResponse)
async def auth(form_data: OAuth2PasswordRequestForm = Depends()):
    print(form_data.__dict__)
    if form_data.client_secret != settings.CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrent client secret"
        )
    user = await User.get_or_none(email=form_data.username)
    if not user or not check_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    existing_token = await Token.filter(user=user).first()
    if existing_token:
        await existing_token.delete()
    token_data = {"sub": form_data.username}
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")
    expiry = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    token_obj = await Token.create(user=user, access_token=token, expires=expiry)
    return await TokenResponse.from_tortoise_orm(token_obj)


@router.get("/users/me/", response_model=UserResponse, responses={404: {"model": HTTPNotFoundError}})
async def read_users_me(token: str = Depends(oauth2_scheme)):
    token_obj = await Token.get(access_token=token)
    user = token_obj.user
    return await UserResponse.from_queryset_single(user)
