from fastapi import APIRouter

from api.auth.cookies_oauth import CookieUserSchema
from api.auth.models import User
from api.subscriptions.models import SubscriptionPlan


UserResponse = User.get_pydantic()
SubscriptionResponse = SubscriptionPlan.get_pydantic()
oauth2_scheme = CookieUserSchema(tokenUrl="/api/auth")
router = APIRouter(tags=['Subscription'], prefix='/subscription')


@router.get('/list')
async def subscriptions_list():
    return await SubscriptionResponse.from_queryset(SubscriptionPlan.all())
