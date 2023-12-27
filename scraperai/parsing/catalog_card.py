import json
import logging

from scraperai.llm import OpenAIChatModel

logger = logging.getLogger(__file__)


class CatalogCardParser:
    def __init__(self, chat_model: OpenAIChatModel):
        self.chat_model = chat_model
        self.total_spent = 0.0

    def find_fields(self, html_snippet: str) -> dict[str, dict[str, str]]:
        system_prompt = "You are an HTML parser. Your primary goal is to find fields with data."
        prompt = """
            This HTML snippet contains information about one product or service. 
            Some fields have keys and values, others have only values (for example product's name). 
            Detect fields with keys and without keys and return them separatly in a form of json:
            ```
            {
              "fields_with_keys": {
                  "key from html": "value from html",
              },
              "fields_without_keys": {
                 "guess key": "value from html",
              }
            }
            ```
            The HTML: %s
        """ % html_snippet

        response = self.chat_model.get_answer(prompt, system_prompt, force_json=True)
        self.total_spent += response.price
        try:
            data = json.loads(response.text)
            if not isinstance(data, dict):
                raise TypeError
            return data
        except Exception as e:
            logger.exception(e)
            raise e

    def find_xpath_selectors(self, html_snippet: str, fields: dict[str, dict[str, str]]):
        all_keys = list(fields['fields_with_keys'].keys()) + \
                   list(fields['fields_with_keys'].values()) +\
                   list(fields['fields_without_keys'].values())
        keys_str = ','.join([f'"{x}"' for x in all_keys])
        system_prompt = "Your primary goal is to find XPath selectors."
        prompt = """
            This HTML snippet contains information about one product or service. 
            Find XPATH selectors for the following keys: %s. Return result in a form of json dictionary:
            ```
            {
                "key": "xpath selector",
                ...
            }
            ```
            The HTML: %s
        """ % (keys_str, html_snippet)
        response = self.chat_model.get_answer(prompt, system_prompt, force_json=True)
        self.total_spent += response.price
        return response.text


def test():
    from tests.settings import BASE_DIR, OPEN_AI_TOKEN
    data = {'fields_with_keys': {'Тип': 'Наушники', 'Наличие микрофона': 'Да', 'Конструкция наушников': 'Внутриканальные', 'Шумоподавление': 'Активное', 'Время работы в режиме разговора, ч': '6', 'Цена': '1\u2009299\u2009₽', 'Старая цена': '14\u2009990\u2009₽', 'Скидка': '−91%', 'Остаток': 'Осталось 89 шт', 'Рейтинг': '4.7', 'Количество отзывов': '178 отзывов', 'Доставка': 'Послезавтра'}, 'fields_without_keys': {'Название': 'Наушники беспроводные, bluetooth наушники, tws наушники, беспроводные наушники с микрофоном, беспроводные наушники', 'Акция': 'РАСПРОДАЖА'}}
    parser = CatalogCardParser(OpenAIChatModel(OPEN_AI_TOKEN))

    with open(BASE_DIR / 'tests' / 'data' / 'ozon_card.html', 'r') as f:
        html_str = f.read()

    result = parser.find_xpath_selectors(html_snippet=html_str, fields=data)
    print(result)


if __name__ == '__main__':
    test()
