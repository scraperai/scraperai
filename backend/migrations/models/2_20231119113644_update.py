from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "scrapingtask" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "status" VARCHAR(7) NOT NULL  /* RUNNING: RUNNING\nWAIT: WAIT */,
    "step" VARCHAR(9) NOT NULL  /* INIT: INIT\nDETECTION: DETECTION\nPAYMENT: PAYMENT\nSCRAPING: SCRAPING */,
    "sources" JSON NOT NULL,
    "temp_results" JSON,
    "updated_at" TIMESTAMP NOT NULL,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "transaction_id" INT REFERENCES "transaction" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "scrapingtask";"""
