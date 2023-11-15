from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from api.auth.cookies_oauth import CookieUserSchema
from api.payments.api_models import PaymentCreationForm, TinkoffNotification
from api.payments.services.base.dto import BasePaymentInfo
from api.payments.services.payment_service import PaymentProvider, PaymentService
from models.auth.models import User
from models.payments.models import Order


OrderResponse = Order.get_pydantic()
strict_user_schema = CookieUserSchema(tokenUrl="/api/auth", auto_error=True)
user_schema = CookieUserSchema(tokenUrl="/api/auth", auto_error=False)
router = APIRouter(tags=['Payments'], prefix='/payment')


@router.post("/create", response_model=BasePaymentInfo)
async def create(form: PaymentCreationForm, user: User = Depends(strict_user_schema)):
    provider = PaymentProvider.by_currency(form.currency)
    service = PaymentService(provider)
    return await service.create_order(user, form)


@router.get("/list")
async def orders_list(user: User = Depends(strict_user_schema)):
    return await OrderResponse.from_queryset(user.orders.all())


@router.get("/status/{payment_id}")
async def check_status(payment_id: int, user: User = Depends(strict_user_schema)):
    if payment_id == -1:
        order = await user.orders.order_by('-updated_at').first()
    else:
        order = await Order.get_or_none(payment_id=payment_id)
        if order is None:
            order = await Order.get(pk=payment_id)
    provider = PaymentProvider.by_currency(order.currency)
    service = PaymentService(provider)
    order = await service.check_status(order)
    return await OrderResponse.from_tortoise_orm(order)


@router.post("/tinkoff-notifications")
async def notifications(form: TinkoffNotification):
    order = await Order.get(payment_id=form.payment_id)
    provider = PaymentProvider.by_currency(order.currency)
    service = PaymentService(provider)
    await service.on_status_change(order, form.status)

    return HTMLResponse(content='OK', status_code=200)
