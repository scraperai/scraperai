from pydantic import BaseModel, Field

from models.payments import OrderStatus, Currency


class PaymentCreationForm(BaseModel):
    amount: int
    currency: Currency = Field(default=Currency.RUB)


class TinkoffNotification(BaseModel):
    order_id: str = Field(alias='OrderId')
    success: bool = Field(alias='Success')
    status: OrderStatus = Field(alias='Status')
    payment_id: str = Field(alias='PaymentId')
