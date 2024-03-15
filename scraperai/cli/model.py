import enum
from typing import Optional, Literal

from pydantic import BaseModel


class CardEditFormModel(BaseModel):
    has_changes: bool
    new_card_xpath: Optional[str] = None
    new_url_xpath: Optional[str] = None
    user_suggestion: Optional[str] = None


class FieldsEditFormModel(BaseModel):
    has_changes: bool
    action_type: Literal['a', 'r'] = 'a'
    user_suggestion: Optional[str] = None
    field_to_delete: Optional[str] = None


class ScreenStatus(enum.Enum):
    loading = 'loading'
    show = 'show'
    edit = 'edit'
