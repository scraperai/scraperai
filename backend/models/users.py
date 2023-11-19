from __future__ import annotations

import datetime
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model
from fastapi_admin.models import AbstractAdmin


class User(AbstractAdmin):
    email = fields.CharField(max_length=255, null=True)
    full_name = fields.CharField(max_length=255, null=True)
    verification_code = fields.CharField(max_length=64, null=True)
    balance = fields.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = fields.DatetimeField(default=datetime.datetime.now)
    created_at = fields.DatetimeField(auto_now_add=True)
    roles = fields.ManyToManyField('models.Role', related_name='users')

    def __str__(self):
        return self.email

    @property
    async def roles_set(self) -> set[str]:
        return {x.key for x in await self.roles.all()}

    @staticmethod
    def get_pydantic():
        return pydantic_model_creator(User, exclude=('username', 'password', 'verification_code'))

    @staticmethod
    async def create_defaults():
        user, _ = await User.get_or_create(
            username='admin@example.com',
            defaults={
                'email': 'admin@example.com',
                'password': 'password',
                'full_name': 'Admin',
            }
        )
        role = await Role.get(key='admin')
        await user.roles.add(role)


class Role(Model):
    key = fields.CharField(max_length=256)
    name = fields.CharField(max_length=256)

    def __str__(self):
        return self.name

    @staticmethod
    async def create_defaults():
        roles = [('admin', 'Administrator'), ('client', 'Client')]
        for role in roles:
            key, name = role
            await Role.get_or_create(key=key, name=name)


class Feedback(Model):
    user = fields.ForeignKeyField('models.User', related_name='feedback', null=True)
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
