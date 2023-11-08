from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "config" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "label" VARCHAR(200) NOT NULL,
    "key" VARCHAR(20) NOT NULL UNIQUE /* Unique key for config */,
    "value" JSON NOT NULL,
    "status" SMALLINT NOT NULL  DEFAULT 1 /* on: 1\noff: 0 */
);
CREATE TABLE IF NOT EXISTS "subscriptionplan" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(255) NOT NULL UNIQUE,
    "price" INT NOT NULL  /* Price per period */,
    "currency" VARCHAR(3) NOT NULL  /* RUB: RUB\nUSD: USD */,
    "duration" INT NOT NULL  /* Duration in days */,
    "updated_at" TIMESTAMP NOT NULL,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "user" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "username" VARCHAR(50) NOT NULL UNIQUE,
    "password" VARCHAR(200) NOT NULL,
    "email" VARCHAR(255),
    "full_name" VARCHAR(255),
    "verification_code" VARCHAR(64),
    "updated_at" TIMESTAMP NOT NULL,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "subscription_id" INT REFERENCES "subscriptionplan" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "token" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "access_token" VARCHAR(255) NOT NULL UNIQUE,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "expires" TIMESTAMP NOT NULL,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
