from fastapi import APIRouter, Depends, HTTPException
from starlette import status

import tasks
from api.api_models import SuccessResponse
from api.auth.oauth.schemas import OAuthSchemasBuilder
from api.scraping.api_models import TaskInitForm, TaskTuneForm, TuneType
from api.session.schema import SessionSchema
from models.scraping import ScrapingTask
from models.users import User


session_schema = SessionSchema(auto_error=True)
user_schema = OAuthSchemasBuilder.build(auto_error=True)
TaskResponse = ScrapingTask.get_pydantic()
router = APIRouter(tags=['Scraping'], prefix='/scraping')


@router.post("/init")
async def init_task(form: TaskInitForm, session_id: str = Depends(session_schema)):
    task = await ScrapingTask.create(
        session_id=session_id,
        status=ScrapingTask.Status.RUNNING,
        step=ScrapingTask.Step.INIT,
        sources=form.model_dump(mode='json')
    )

    iq_task = await tasks.init_scraping_task.kiq(form.url.__str__(), task.pk)
    task.celery_task_id = iq_task.task_id
    await task.save()
    return await TaskResponse.from_tortoise_orm(task)


@router.get("/status/{task_id}")
async def get_status(task_id: int, session_id: str = Depends(session_schema)):
    task = await ScrapingTask.get(pk=task_id)
    return await TaskResponse.from_tortoise_orm(task)


@router.post("/forward/{task_id}")
async def forward(task_id: int, session_id: str = Depends(session_schema)):
    task = await ScrapingTask.get(pk=task_id)
    if task.status == ScrapingTask.Status.RUNNING:
        raise HTTPException(status_code=status.HTTP_425_TOO_EARLY, detail="Task is still running")
    if task.step == ScrapingTask.Step.DETECTION:
        task.status = ScrapingTask.Status.RUNNING
        task.step = ScrapingTask.Step.PAYMENT
        await task.save()
    elif task.step == ScrapingTask.Step.PAYMENT:
        task.status = ScrapingTask.Status.RUNNING
        task.step = ScrapingTask.Step.SCRAPING
        await task.save()
    elif task.step == ScrapingTask.Step.SCRAPING:
        task.step = ScrapingTask.Step.DONE
        await task.save()
    else:
        return await TaskResponse.from_tortoise_orm(task)


@router.post("/tune/{task_id}")
async def tune(task_id: int, form: TaskTuneForm, user: User = Depends(user_schema)):
    if form.type == TuneType.PAGE_TYPE:
        await tasks.change_page_type(form.user_input, task_id)
    elif form.type == TuneType.PRODUCT_CARD:
        await tasks.change_product_card(form.user_input, task_id)
    elif form.type == TuneType.PAGINATION:
        await tasks.change_pagination(form.user_input, task_id)
    elif form.type == TuneType.PRODUCT_CARD_FIELDS:
        pass
    elif form.type == TuneType.NESTED_PAGE_FIELDS:
        pass

    return SuccessResponse()
