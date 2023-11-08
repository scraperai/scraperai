from pydantic import BaseModel, EmailStr

from api.api_models import SuccessResponse


class UserSignupForm(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class PasswordChangeForm(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str


class PasswordResetResponse(SuccessResponse):
    new_password: str
