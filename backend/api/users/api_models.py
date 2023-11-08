from typing import Optional

from pydantic import BaseModel, EmailStr


class FeedbackForm(BaseModel):
    email: Optional[EmailStr]
    name: Optional[str]
    text: str
