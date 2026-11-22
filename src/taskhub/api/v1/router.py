from fastapi import APIRouter

from .auth import router as auth_router
from .project import router as project_router
from .users import router as user_router
from .workspace import router as workspace_router

router = APIRouter(prefix="/api/v1")

router.include_router(user_router)
router.include_router(auth_router)
router.include_router(workspace_router)
router.include_router(project_router)
