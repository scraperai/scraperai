from __future__ import annotations

import datetime

import jwt
from fastapi_admin.models import AbstractAdmin
from fastapi_admin.utils import hash_password
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model

import settings


class User(AbstractAdmin):
    email = fields.CharField(max_length=255, null=True)
    full_name = fields.CharField(max_length=255, null=True)
    verification_code = fields.CharField(max_length=64, null=True)
    updated_at = fields.DatetimeField(default=datetime.datetime.now)
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    @classmethod
    async def from_token(cls, token: str) -> User | None:
        token = await Token.get_or_none(access_token=token)
        if token is None:
            return None
        await token.fetch_related('user')
        return token.user

    @staticmethod
    def get_pydantic():
        return pydantic_model_creator(User, exclude=('username', 'password', 'verification_code'))

    @staticmethod
    async def create_defaults():
        await User.get_or_create(
            username='admin@example.com',
            defaults={
                'email': 'admin@example.com',
                'password': hash_password('password'),
                'full_name': 'Admin'
            }
        )


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

    @staticmethod
    def get_pydantic():
        return pydantic_model_creator(Token, exclude=('user', 'created'))
