from fastapi import APIRouter
from api.auth.routes import router as auth_router


router = APIRouter()
router.include_router(auth_router)


@router.get('/')
def index():
    return {'status': 'success'}
