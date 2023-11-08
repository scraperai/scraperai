import os
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

import settings
import admin
import api


app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(settings.BASE_DIR, "static")),
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
app.include_router(api.router, prefix='/api')

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

register_tortoise(app, config=settings.TORTOISE_ORM, generate_schemas=False)


@app.on_event("startup")
async def startup():
    await admin.on_startup()


@app.get("/")
async def index():
    return RedirectResponse(url="/admin")
