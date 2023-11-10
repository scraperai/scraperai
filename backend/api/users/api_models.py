from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class FeedbackForm(BaseModel):
    email: Optional[EmailStr] = Field(None, description='Pass for non-authorized users')
    name: Optional[str] = Field(None, description='Pass for non-authorized users')
    text: str
