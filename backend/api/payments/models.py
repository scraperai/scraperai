from __future__ import annotations

import datetime
import enum
from tortoise import fields
from tortoise.models import Model


class Currency(str, enum.Enum):
    RUB = 'RUB'
    USD = 'USD'


class OrderStatus(str, enum.Enum):
    NEW = 'NEW'
    AWAIT_PAYMENT = 'AWAIT_PAYMENT'
    AWAIT_RESERVATION = 'AWAIT_RESERVATION'
    RESERVATION_SUCCESS = 'RESERVATION_SUCCESS'
    PAYMENT_SUCCESS = 'PAYMENT_SUCCESS'
    WITHOUT_DOCS = 'WITHOUT_DOCS'
    ON_APPROVAL = 'ON_APPROVAL'
    APPROVAL_SUCCESS = 'APPROVAL_SUCCESS'
    VERIFY_FAILED = 'VERIFY_FAILED'
    AWAIT_CONFIRM_PAYMENT = 'AWAIT_CONFIRM_PAYMENT'
    CONFIRM_PAYMENT_FAILED = 'CONFIRM_PAYMENT_FAILED'
    BOOKED = 'BOOKED'
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'
    CANCELED = 'CANCELED'
    REJECTED = 'REJECTED'
    ON_REINIT = 'ON_REINIT'
    REINIT_FAILED = 'REINIT_FAILED'
    PAYMENT_SESSION_EXPIRED = 'PAYMENT_SESSION_EXPIRED'


class Order(Model):
    user = fields.ForeignKeyField('models.User', related_name='orders')
    status = fields.CharEnumField(enum_type=OrderStatus)
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    currency = fields.CharEnumField(enum_type=Currency, default=Currency.RUB)
    updated_at = fields.DatetimeField(default=datetime.datetime.now)
    created_at = fields.DatetimeField(auto_now_add=True)
