from __future__ import annotations
import enum

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
