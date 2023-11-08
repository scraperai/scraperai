from fastapi import APIRouter, Depends

from api.api_models import SuccessResponse
from api.auth.cookies_oauth import CookieUserSchema
from api.auth.models import User
from api.users.api_models import FeedbackForm
from api.users.models import Feedback


UserResponse = User.get_pydantic()
oauth2_scheme = CookieUserSchema(tokenUrl="/api/auth")
router = APIRouter(tags=['User'], prefix='/users')


@router.get("/me", response_model=UserResponse)
async def read_users_me(user: User = Depends(oauth2_scheme)):
    return await UserResponse.from_tortoise_orm(user)


@router.post('/feedback')
async def feedback(form: FeedbackForm):
    await Feedback.create(
        name=form.name,
        email=form.email,
        text=form.text
    )
    return SuccessResponse()
