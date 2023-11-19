import os

from fastapi_admin.app import app
from fastapi_admin.file_upload import FileUpload
from fastapi_admin.resources import Dropdown, Field, Link, Model
from fastapi_admin.widgets import filters, inputs

from models.users import User
from models.users import Feedback
from settings import BASE_DIR

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
