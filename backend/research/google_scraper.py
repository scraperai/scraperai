import datetime

import numpy as np
import pandas as pd
from functools import reduce

import requests
import time


SECRET_KEY = '5c05Bc1ByV0FxOGNTVjJrR0gydzJLST0'
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded',
}
params = {
    'key': SECRET_KEY
}


def create_search_task(keywords: list[str], lang: str) -> str:
    words = ["keywords[]=" + w.replace(' ', '%20') for w in keywords]

    data = ('&'.join(words) + f'&engine=google&device=desktop&language={lang}').encode()
    url = 'https://line.pr-cy.ru/api/v1.1.0/task/create'
    response = requests.post(url, params=params, headers=headers, data=data)
    return response.json()['taskId']


def get_task_status(task_id: str) -> str:
    url = f'https://line.pr-cy.ru/api/v1.1.0/task/status/{task_id}'
    response = requests.get(url, params=params, headers=headers)
    return response.json()['status']


def get_task_result(task_id: str) -> dict:
    url = f'https://line.pr-cy.ru/api/v1.1.0/task/result/{task_id}'
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    values = {
        x['query']: [d['url'] for d in x['serp']]
        for x in data['keywords']
    }
    return values


def search_google(keywords: list[str], lang: str = 'ru', timeout: float = 60):
    task_id = create_search_task(keywords, lang)
    created_at = datetime.datetime.now()
    while (datetime.datetime.now() - created_at).seconds < timeout:
        time.sleep(10)
        status = get_task_status(task_id)
        print(f'Status of task "{task_id}" is "{status}"')
        if status == 'done':
            time.sleep(5)
            break
    urls = get_task_result(task_id)
    return urls


def main():
    filename = 'files/dataset.xlsx'
    keywords = ['Buy iPhone']
    response = search_google(keywords, lang='en')
    urls_list = reduce(lambda x, y: x + y, list(response.values()), [])
    print(urls_list)
    print(f'Collected {len(urls_list)} urls')
    new_df = pd.DataFrame({'URL': urls_list, 'Category': np.zeros(len(urls_list))})
    df = pd.read_excel(filename, sheet_name='data')
    df = pd.concat([df, new_df])
    df.to_excel(filename, sheet_name='data', index=False)


if __name__ == '__main__':
    main()
