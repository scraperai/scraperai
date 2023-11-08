from tortoise import fields
from tortoise.models import Model


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
