import httpx

from api.payments.services.request_signer import TinkoffPaymentsRequestSigner


def build_init_payload(amount: int, order_id: str) -> dict:
    return {
        'Amount': amount,
        'OrderId': order_id,
        'PayType': 'O',
    }


class TinkoffPaymentsApiClient:
    def __init__(self, base_url: str, terminal_key: str, password: str):
        self.__request_signer = TinkoffPaymentsRequestSigner(password)
        self.__base_url = base_url
        self.__terminal_key = terminal_key

    def _request(self, path: str, data: dict) -> dict:
        data['TerminalKey'] = self.__terminal_key
        token = self.__request_signer.generate_sign(data)
        data['Token'] = token
        response = httpx.request(
            method='post',
            url=f'{self.__base_url}/{path}',
            json=data
        )
        response.raise_for_status()
        response = response.json()
        if not response['Success']:
            raise Exception(f'Invalid Tinkoff Payment response - {response}')
        return response

    def init(self, amount: int, order_id: str) -> dict:
        return self._request('Init', build_init_payload(amount, order_id))

    def get_state(self, payment_id: int) -> dict:
        return self._request('GetState', data={'PaymentId': payment_id})

    def check_order(self, order_id):
        return self._request('CheckOrder', data={'OrderId': order_id})


def test():
    import settings
    api = TinkoffPaymentsApiClient(
        base_url=settings.TINKOFF_API_URL,
        terminal_key=settings.TINKOFF_TERMINAL_KEY,
        password=settings.TINKOFF_PASSWORD
    )
    # response = api.init(amount=100, order_id='Test2')
    # print(response)
    response = api.check_order('Test0')
    print(response)
    # response = api.get_state(3518891893)
    # print(response)


if __name__ == '__main__':
    test()
