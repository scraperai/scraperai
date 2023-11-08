from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "token" RENAME COLUMN "token" TO "access_token";
        ALTER TABLE "token" RENAME COLUMN "expires_at" TO "expires";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "token" RENAME COLUMN "expires" TO "expires_at";
        ALTER TABLE "token" RENAME COLUMN "access_token" TO "token";"""
