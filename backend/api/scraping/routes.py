from fastapi import APIRouter, Depends

from api.auth.oauth.schemas import OAuthSchemasBuilder
from api.scraping.api_models import TaskInitForm
from models.scraping import ScrapingTask
from models.users import User


user_schema = OAuthSchemasBuilder.build(auto_error=True)
TaskResponse = ScrapingTask.get_pydantic()
router = APIRouter(tags=['Scraping'], prefix='/scraping')


@router.post("/init")
async def init_task(form: TaskInitForm, user: User = Depends(user_schema)):
    task = await ScrapingTask.create(
        user=user,
        status=ScrapingTask.Status.RUNNING,
        step=ScrapingTask.Step.INIT,
        sources=form.model_dump()
    )
    return await TaskResponse.from_tortoise_orm(task)


@router.get("/status/{task_id}")
async def get_status(task_id: int, user: User = Depends(user_schema)):
    task = await ScrapingTask.get(pk=task_id)
    return await TaskResponse.from_tortoise_orm(task)


@router.post("/forward")
async def forward(user: User = Depends(user_schema)):
    return {}


@router.post("/tune")
async def tune(user: User = Depends(user_schema)):
    return {}
