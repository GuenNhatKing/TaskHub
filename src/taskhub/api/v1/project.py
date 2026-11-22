import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from taskhub.core.dependencies import (
    CurrentUser,
    get_project_service,
)
from taskhub.schemas.project import ProjectResponse, ProjectUpdateRequest
from taskhub.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
async def get_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[ProjectService, Depends(get_project_service)],
):
    return await services.get_project_detail(project_id, current_user)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
async def update_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    update_request: ProjectUpdateRequest,
    services: Annotated[ProjectService, Depends(get_project_service)],
):
    return await services.update_project(project_id, current_user, update_request)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[ProjectService, Depends(get_project_service)],
):
    return await services.delete_project(project_id, current_user)


@router.post(
    "/{project_id}/archive",
    status_code=status.HTTP_200_OK,
)
async def archive_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[ProjectService, Depends(get_project_service)],
):
    return await services.archive_project(project_id, current_user)


@router.post(
    "/{project_id}/unarchive",
    status_code=status.HTTP_200_OK,
)
async def unarchive_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[ProjectService, Depends(get_project_service)],
):
    return await services.unarchive_project(project_id, current_user)
