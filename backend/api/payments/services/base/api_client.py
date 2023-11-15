from abc import ABC, abstractmethod

from api.payments.services.base.dto import BasePaymentInfo, OrderStatus


class PaymentApiClient(ABC):
    @abstractmethod
    async def init(self, amount: float, order_id: str) -> BasePaymentInfo:
        """Initializes payment"""
        ...

    @abstractmethod
    async def get_state(self, payment_id: str) -> OrderStatus:
        """Return payment's status"""
        ...
