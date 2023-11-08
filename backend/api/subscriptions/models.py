from __future__ import annotations

import datetime
import enum
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class Currency(str, enum.Enum):
    RUB = 'RUB'
    USD = 'USD'


class SubscriptionPlan(Model):
    name = fields.CharField(max_length=255, unique=True)
    price = fields.IntField(description='Price per period')
    currency = fields.CharEnumField(enum_type=Currency)
    duration = fields.IntField(description='Duration in days')
    updated_at = fields.DatetimeField(default=datetime.datetime.now)
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @staticmethod
    def get_pydantic():
        return pydantic_model_creator(SubscriptionPlan, exclude=('updated_at', 'created_at'))

    @staticmethod
    async def create_defaults():
        await SubscriptionPlan.get_or_create(
            name='basic',
            defaults={'price': 5000, 'duration': 30, 'currency': Currency.RUB}
        )
        await SubscriptionPlan.get_or_create(
            name='extended',
            defaults={'price': 20000, 'duration': 30, 'currency': Currency.RUB}
        )
