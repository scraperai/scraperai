from pydantic import BaseModel


class BaseResponse(BaseModel):
    status: str


class SuccessResponse(BaseResponse):
    status: str = 'success'
