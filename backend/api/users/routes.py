from fastapi import APIRouter, Depends

from api.api_models import SuccessResponse
from api.auth.cookies_oauth import CookieUserSchema
from models.auth.models import User
from api.users.api_models import FeedbackForm
from models.users.models import Feedback


UserResponse = User.get_pydantic()
strict_user_schema = CookieUserSchema(tokenUrl="/api/auth", auto_error=True)
user_schema = CookieUserSchema(tokenUrl="/api/auth", auto_error=False)
router = APIRouter(tags=['User'], prefix='/users')


@router.get("/me", response_model=UserResponse)
async def read_users_me(user: User = Depends(strict_user_schema)):
    return await UserResponse.from_tortoise_orm(user)


@router.post('/feedback')
async def feedback(form: FeedbackForm, user: User = Depends(user_schema)):
    if user:
        await Feedback.create(
            user=user,
            text=form.text
        )
    else:
        await Feedback.create(
            name=form.name,
            email=form.email,
            text=form.text
        )
    return SuccessResponse()
