from __future__ import annotations

import datetime

import jwt
from tortoise import fields
from tortoise.models import Model
from fastapi import Response

import settings


class User(Model):
    email = fields.CharField(max_length=255, unique=True)
    full_name = fields.CharField(max_length=255, null=True)
    password = fields.CharField(max_length=255)

    def __str__(self):
        return self.email


class Token(Model):
    user = fields.ForeignKeyField('models.User', related_name='tokens')
    access_token = fields.CharField(max_length=255, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    expires = fields.DatetimeField()

    @classmethod
    async def get_for_user(cls, user: User) -> Token:
        existing_token = await cls.filter(user=user).first()
        if existing_token:
            await existing_token.delete()
        token_data = {"sub": user.email}
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")
        expiry = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        return await cls.create(user=user, access_token=token, expires=expiry)
