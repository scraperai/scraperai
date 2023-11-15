import os
from typing import List

from starlette.requests import Request

from api.users.models import Feedback
from settings import BASE_DIR
from admin.models import Config, Status
from fastapi_admin.app import app
from fastapi_admin.enums import Method
from fastapi_admin.file_upload import FileUpload
from fastapi_admin.resources import Action, Dropdown, Field, Link, Model, ToolbarAction
from fastapi_admin.widgets import displays, filters, inputs
from api.auth.models import User


upload = FileUpload(uploads_dir=os.path.join(BASE_DIR, "../static", "uploads"))


@app.register
class Dashboard(Link):
    label = "Dashboard"
    icon = "fas fa-home"
    url = "/admin"


@app.register
class UserResource(Model):
    label = "Users"
    model = User
    icon = "fas fa-user"
    page_pre_title = "Users"
    page_title = "User"
    filters = [
        filters.Search(
            name="email",
            label="Email",
            search_mode="contains",
            placeholder="Search for email",
        ),
        filters.Date(name="created_at", label="CreatedAt"),
    ]
    fields = [
        "id",
        Field(name="email", label="Email", input_=inputs.Email()),
        "full_name",
        "created_at",
        "updated_at"
    ]


@app.register
class ConfigResource(Model):
    label = "Config"
    model = Config
    icon = "fas fa-cogs"
    filters = [
        filters.Enum(enum=Status, name="status", label="Status"),
        filters.Search(name="key", label="Key", search_mode="equal"),
    ]
    fields = [
        "id",
        "label",
        "key",
        "value",
        Field(
            name="status",
            label="Status",
            input_=inputs.RadioEnum(Status, default=Status.on),
        ),
    ]

    async def row_attributes(self, request: Request, obj: dict) -> dict:
        if obj.get("status") == Status.on:
            return {"class": "bg-green text-white"}
        return await super().row_attributes(request, obj)

    async def get_actions(self, request: Request) -> List[Action]:
        actions = await super().get_actions(request)
        switch_status = Action(
            label="Switch Status",
            icon="ti ti-toggle-left",
            name="switch_status",
            method=Method.PUT,
        )
        actions.append(switch_status)
        return actions


@app.register
class Content(Dropdown):

    class FeedbackResource(Model):
        label = "Feedback"
        model = Feedback
        filters = []
        fields = [
            "name",
            "email",
            "text",
            "created_at"
        ]

    label = "Content"
    icon = "fas fa-bars"
    resources = [FeedbackResource]


@app.register
class GithubLink(Link):
    label = "Github"
    url = "https://github.com/iakov-kaiumov/scraper-ai"
    icon = "fab fa-github"
    target = "_blank"


@app.register
class DocumentationLink(Link):
    label = "Documentation"
    url = "/docs"
    icon = "fas fa-file-code"
    target = "_blank"
