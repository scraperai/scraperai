from fastapi import APIRouter, Depends
from tortoise.contrib.pydantic import pydantic_model_creator

from api.auth.cookies_oauth import OAuth2PasswordBearerWithCookie
from api.auth.models import User

UserResponse = User.get_pydantic()
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/auth")
router = APIRouter(tags=['User'], prefix='/users')


@router.get("/me/", response_model=UserResponse)
async def read_users_me(token: str = Depends(oauth2_scheme)):
    user = await User.from_token(token)
    return await UserResponse.from_tortoise_orm(user)
