from tortoise import Model, fields
from enum import IntEnum


class Status(IntEnum):
    on = 1
    off = 0


class Config(Model):
    label = fields.CharField(max_length=200)
    key = fields.CharField(max_length=20, unique=True, description="Unique key for config")
    value = fields.JSONField()
    status: Status = fields.IntEnumField(Status, default=Status.on)
