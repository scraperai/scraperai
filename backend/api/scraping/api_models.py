import enum

from pydantic import BaseModel, AnyHttpUrl, Field


class TuneType(str, enum.Enum):
    PAGE_TYPE = 'PAGE_TYPE'
    PRODUCT_CARD = 'PRODUCT_CARD'
    PAGINATION = 'PAGINATION'
    PRODUCT_CARD_FIELDS = 'PRODUCT_CARD_FIELDS'
    NESTED_PAGE_FIELDS = 'NESTED_PAGE_FIELDS'


class TaskInitForm(BaseModel):
    url: AnyHttpUrl


class TaskTuneForm(BaseModel):
    type: TuneType = Field(...)
    user_input: str

    class Config:
        use_enum_values = True
