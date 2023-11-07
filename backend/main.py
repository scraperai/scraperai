import os
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

from settings import BASE_DIR, DATABASE_URL
import admin

app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

admin.register(app)

register_tortoise(
    app,
    config={
        "connections": {"default": DATABASE_URL},
        "apps": {
            "models": {
                "models": ["admin.models"],
                "default_connection": "default",
            }
        },
    },
    generate_schemas=True,
)


@app.on_event("startup")
async def startup():
    await admin.on_startup()


@app.get("/")
async def index():
    return RedirectResponse(url="/admin")

