from fastapi import APIRouter, Depends

from api.auth.oauth.schemas import OAuthSchemasBuilder
from models.users import User
from models.payments import Transaction


user_schema = OAuthSchemasBuilder.build(auto_error=True)
router = APIRouter(tags=['Scraping'], prefix='/scraping')


@router.post("/test",)
async def test(user: User = Depends(user_schema)):
    return {}
