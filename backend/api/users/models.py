from __future__ import annotations

import datetime
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class Feedback(Model):
    email = fields.CharField(max_length=256, null=True)
    name = fields.CharField(max_length=256, null=True)
    text = fields.TextField()
    updated_at = fields.DatetimeField(default=datetime.datetime.now)
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.pk}_{self.text[:20]}'

    @classmethod
    def get_pydantic(cls):
        return pydantic_model_creator(cls)
