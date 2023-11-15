import asyncio

import httpx

from api.payments.services.base.api_client import PaymentApiClient
from api.payments.services.base.dto import OrderStatus, BasePaymentInfo
from api.payments.services.tinkoff.request_signer import TinkoffPaymentsRequestSigner


def build_init_payload(amount: int, order_id: str) -> dict:
    return {
        'Amount': amount,
        'OrderId': order_id,
        'PayType': 'O',
    }


class TinkoffApiClient(PaymentApiClient):
    def __init__(self, base_url: str, terminal_key: str, password: str):
        self.__request_signer = TinkoffPaymentsRequestSigner(password)
        self.__base_url = base_url
        self.__terminal_key = terminal_key

    async def _request(self, path: str, data: dict) -> dict:
        data['TerminalKey'] = self.__terminal_key
        token = self.__request_signer.generate_sign(data)
        data['Token'] = token
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method='post',
                url=f'{self.__base_url}/{path}',
                json=data
            )
        response.raise_for_status()
        response = response.json()
        if not response['Success']:
            raise Exception(f'Invalid Tinkoff Payment response - {response}')
        return response

    async def init(self, amount: float, order_id: str) -> BasePaymentInfo:
        response = await self._request('Init', build_init_payload(int(amount * 100), order_id))
        return BasePaymentInfo(
            status=OrderStatus(response['Status']),
            payment_id=str(response['PaymentId']),
            url=response['PaymentURL']
        )

    async def get_state(self, payment_id: str) -> OrderStatus:
        response = await self._request('GetState', data={'PaymentId': int(payment_id)})
        return OrderStatus(response['Status'])


async def test():
    import settings
    api = TinkoffApiClient(
        base_url=settings.TINKOFF_API_URL,
        terminal_key=settings.TINKOFF_TERMINAL_KEY,
        password=settings.TINKOFF_PASSWORD
    )
    response = await api.init(amount=100, order_id='Test2')
    print(response)
    # response = api.get_state(3518824360)
    # print(response)
    # response = api.get_state(3518891893)
    # print(response)


if __name__ == '__main__':
    asyncio.run(test())
