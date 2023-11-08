from fastapi import APIRouter
from api.auth import router as auth_router
from api.users import router as users_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(users_router)


@router.get('/')
def index():
    return {'status': 'success'}