from __future__ import annotations

import datetime
import enum

from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class ScrapingTask(Model):
    class Status(str, enum.Enum):
        RUNNING = 'RUNNING'
        WAIT = 'WAIT'

    class Step(str, enum.Enum):
        INIT = 'INIT'
        DETECTION = 'DETECTION'
        PAYMENT = 'PAYMENT'
        SCRAPING = 'SCRAPING'

    user = fields.ForeignKeyField('models.User', related_name='tasks')
    transaction = fields.ForeignKeyField('models.Transaction', related_name='tasks', null=True)
    status = fields.CharEnumField(enum_type=Status)
    step = fields.CharEnumField(enum_type=Step)

    sources = fields.JSONField()
    temp_results = fields.JSONField(null=True)

    updated_at = fields.DatetimeField(default=datetime.datetime.now)
    created_at = fields.DatetimeField(auto_now_add=True)

    @staticmethod
    def get_pydantic():
        return pydantic_model_creator(ScrapingTask, exclude=('user', 'sources', 'temp_results', ))
