from __future__ import annotations

import datetime
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model

from api.payments.services.base.dto import OrderStatus, Currency, PaymentProvider

CREDITS_CONVERTER = {
    Currency.RUB: 1.0,
    Currency.USD: 100.0
}


class Order(Model):
    user = fields.ForeignKeyField('models.User', related_name='orders')
    status = fields.CharEnumField(enum_type=OrderStatus)
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    currency = fields.CharEnumField(enum_type=Currency, default=Currency.RUB)
    multiplicator = fields.FloatField()
    updated_at = fields.DatetimeField(default=datetime.datetime.now)
    created_at = fields.DatetimeField(auto_now_add=True)

    payment_provider = fields.CharEnumField(enum_type=PaymentProvider, default=PaymentProvider.tinkoff)
    payment_id = fields.CharField(max_length=255, null=True)
    payment_url = fields.CharField(max_length=255, null=True)

    @staticmethod
    def get_pydantic():
        return pydantic_model_creator(Order, exclude=('user', ))
