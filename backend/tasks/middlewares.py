from typing import Any
from taskiq import TaskiqMiddleware
from taskiq import TaskiqResult, TaskiqMessage
from tortoise import Tortoise

import settings


class TortoiseMiddleware(TaskiqMiddleware):
    async def startup(self) -> None:
        await Tortoise.init(settings.TORTOISE_ORM)

    async def post_save(self, message: "TaskiqMessage", result: "TaskiqResult[Any]") -> None:
        await Tortoise.close_connections()
