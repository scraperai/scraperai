from __future__ import annotations
import enum

import settings
from api.payments.api_models import PaymentCreationForm
from api.payments.services.base.api_client import PaymentApiClient
from api.payments.services.base.dto import BasePaymentInfo, OrderStatus, PaymentProvider
from api.payments.services.tinkoff import TinkoffApiClient
from models.auth.models import User
from models.payments.models import Order, CREDITS_CONVERTER


class PaymentService:
    api_client: PaymentApiClient = None

    def __init__(self, provider: PaymentProvider):
        self.provider = provider
        if provider == PaymentProvider.tinkoff:
            self.api_client = TinkoffApiClient(
                base_url=settings.TINKOFF_API_URL,
                terminal_key=settings.TINKOFF_TERMINAL_KEY,
                password=settings.TINKOFF_PASSWORD
            )

    async def create_order(self, user: User, form: PaymentCreationForm) -> BasePaymentInfo:
        order = await Order.create(
            user=user,
            status=OrderStatus.BLANK,
            amount=form.amount,
            currency=form.currency,
            multiplicator=CREDITS_CONVERTER[form.currency],
            payment_provider=self.provider
        )
        info = await self.api_client.init(amount=order.amount, order_id=str(order.pk))
        order.status = info.status
        order.payment_id = info.payment_id
        order.payment_url = info.url
        await order.save()
        return info

    async def check_status(self, order: Order) -> Order:
        status = await self.api_client.get_state(order.payment_id)
        order = await self.on_status_change(order, status)
        return order

    async def on_status_change(self, order: Order, new_status: OrderStatus) -> Order:
        order.status = new_status
        await order.save()

        if new_status == OrderStatus.CONFIRMED:
            await order.fetch_related('user')
            user = order.user
            user.balance += order.amount * order.multiplicator
            await user.save()
        else:
            # TODO: Other statuses
            pass
        return order
