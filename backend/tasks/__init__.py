import logging
import time


import settings
from models.scraping import ScrapingTask
from .middlewares import TortoiseMiddleware

from taskiq_redis import RedisAsyncResultBackend, ListQueueBroker


result_backend = RedisAsyncResultBackend(redis_url=settings.REDIS_URL)
broker = ListQueueBroker(url=settings.REDIS_URL).with_result_backend(
    result_backend
).with_middlewares(
    TortoiseMiddleware(),
)


logger = logging.getLogger(__file__)


@broker.task
async def init_scraping_task(url: str, task_pk: int):
    logger.info(f'Recieved url "{url}"')
    time.sleep(5)

    task = await ScrapingTask.get(pk=task_pk)
    task.step = ScrapingTask.Step.DETECTION
    task.status = ScrapingTask.Status.WAIT
    await task.save()

    # TODO: Init Selenoid

    # TODO: Save selenoid VNC url to the DB

    # TODO: Detect page type; update status

    # TODO: Detect product card; update status

    # TODO: Detect pagination; update status


@broker.task
def change_page_type(new_type: str, task_pk: int):
    pass


@broker.task
def change_product_card(user_input: str, task_pk: int):
    pass


@broker.task
def change_pagination(user_input: str, task_pk: int):
    pass


@broker.task
def detect_catalog_card_fields(task_pk: int):
    pass


@broker.task
def detect_nested_page_fields(task_pk: int):
    pass


@broker.task
def collect_data(task_pk: int):
    pass

