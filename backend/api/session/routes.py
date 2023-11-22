import uuid

from fastapi import APIRouter, Response, Depends

from api.api_models import SuccessResponse
from .schema import SessionSchema

router = APIRouter(tags=['Session'], prefix='/session')
schema = SessionSchema(auto_error=True)


def create_unique_session_id() -> str:
    return str(uuid.uuid4())


@router.get("/create")
def create_session(response: Response):
    session_id = create_unique_session_id()
    response.set_cookie(key=SessionSchema.KEY, value=session_id)
    return {SessionSchema.KEY: session_id}


@router.get("/info")
def get_session_data(session_id: str = Depends(schema)):
    return {SessionSchema.KEY: session_id}


@router.get("/close")
def close_session(response: Response):
    response.delete_cookie(key=SessionSchema.KEY)
    return SuccessResponse()
