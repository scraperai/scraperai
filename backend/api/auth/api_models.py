from pydantic import BaseModel, EmailStr


class UserSignupRequestModel(BaseModel):
    email: EmailStr
    password: str
    full_name: str
