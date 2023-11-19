from __future__ import annotations

import enum
import datetime
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model
from pydantic import BaseModel


class Currency(str, enum.Enum):
    RUB = 'RUB'
    USD = 'USD'


class PaymentProvider(str, enum.Enum):
    tinkoff = 'tinkoff'

    @classmethod
    def by_currency(cls, currency: Currency) -> PaymentProvider:
        if currency == Currency.RUB:
            return cls.tinkoff
        else:
            raise NotImplementedError


class OrderStatus(str, enum.Enum):
    BLANK = 'BLANK'
    NEW = 'NEW'
    FORM_SHOWED = 'FORM_SHOWED'
    AUTHORIZING = 'AUTHORIZING'
    DS_CHECKING = '3DS_CHECKING'
    DS_CHECKED = '3DS_CHECKED'
    AUTHORIZED = 'AUTHORIZED'
    CONFIRMING = 'CONFIRMING'
    CONFIRMED = 'CONFIRMED'
    REVERSING = 'REVERSING'
    AWAIT_CONFIRM_PAYMENT = 'AWAIT_CONFIRM_PAYMENT'
    PARTIAL_REVERSED = 'PARTIAL_REVERSED'
    REVERSED = 'REVERSED'
    REFUNDING = 'REFUNDING'
    PARTIAL_REFUNDED = 'PARTIAL_REFUNDED'
    REFUNDED = 'REFUNDED'
    СANCELED = 'СANCELED'
    DEADLINE_EXPIRED = 'DEADLINE_EXPIRED'
    REJECTED = 'REJECTED'
    AUTH_FAIL = 'AUTH_FAIL'


class BasePaymentInfo(BaseModel):
    status: OrderStatus
    payment_id: str
    url: str


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


class TransactionStatus(str, enum.Enum):
    NEW = 'NEW'
    RUNNING = 'RUNNING'
    CONFIRMED = 'CONFIRMED'
    СANCELED = 'СANCELED'


class Transaction(Model):
    user = fields.ForeignKeyField('models.User', related_name='transactions')
    status = fields.CharEnumField(enum_type=TransactionStatus)
    credits_amount = fields.DecimalField(max_digits=10, decimal_places=2)
    updated_at = fields.DatetimeField(default=datetime.datetime.now)
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f'<Transaction: {self.pk} status: {self.status} amount: {self.credits_amount}>'
