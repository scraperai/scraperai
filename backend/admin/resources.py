import os

from fastapi_admin.app import app
from fastapi_admin.file_upload import FileUpload
from fastapi_admin.resources import Dropdown, Field, Link, Model
from fastapi_admin.widgets import filters, inputs

from models.users import User, Role
from models.users import Feedback
from settings import BASE_DIR

upload = FileUpload(uploads_dir=os.path.join(BASE_DIR, "../static", "uploads"))


@app.register
class Dashboard(Link):
    label = "Dashboard"
    icon = "fas fa-home"
    url = "/admin"


@app.register
class Users(Dropdown):
    class UserResource(Model):
        label = "Users"
        model = User
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
            # Field(name="roles", label="roles", input_=inputs.ManyToMany(model=Role)),
            "created_at",
            "updated_at"
        ]

    class RoleResource(Model):
        label = "Roles"
        model = Role
        page_pre_title = "Roles"
        page_title = "Role"
        fields = ["key", "name"]

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

    label = "Users"
    icon = "fas fa-user"
    resources = [UserResource, RoleResource, FeedbackResource]


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
