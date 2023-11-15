from typing import Any
from hashlib import sha256


class TinkoffPaymentsRequestSigner:
    """Класс для подписи запросов к API платежей Тинькофф"""

    _EXCLUDED_PARAM_NAMES = ('Shops', 'Receipt', 'DATA')

    def __init__(self, password: str) -> None:
        """
        Инициализатор класса.

        :param password: Пароль для создания подписи.
        """

        self.__password = password

    def generate_sign(self, request_data: dict[str, Any]) -> str:
        """
        Метод генерации подписи для запроса.

        :param request_data: Данные тела запроса.

        :return: Подпись запроса в виде строки.
        """

        copy_data = request_data.copy()
        copy_data['Password'] = self.__password

        # Отфильтровываем ненужные параметры, сортируем в порядке убывания
        # ключей, приводим к словарю.
        cleaned_data = dict(
            sorted(
                filter(
                    lambda param: param[0] not in self._EXCLUDED_PARAM_NAMES,
                    copy_data.items(),
                ),
                key=lambda param: param[0],
            )
        )

        concatenated_values = ''.join(map(str, cleaned_data.values()))
        concatenated_values = concatenated_values.replace('True', 'true').replace('False', 'false')

        return sha256(concatenated_values.encode()).hexdigest()
