import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from taskhub.core.dependencies import CurrentUser, get_workspace_service
from taskhub.schemas.project import ProjectCreateRequest, ProjectResponse
from taskhub.schemas.workspace import (
    WorkspaceAddMemberRequest,
    WorkspaceCreateRequest,
    WorkspaceMemberResponse,
    WorkspaceResponse,
    WorkspaceUpdateRequest,
)
from taskhub.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    current_user: CurrentUser,
    create_workspace_request: WorkspaceCreateRequest,
    services: Annotated[WorkspaceService, Depends(get_workspace_service)],
):
    return await services.create_new_workspace(current_user, create_workspace_request)


@router.get(
    "/{workspace_id}", response_model=WorkspaceResponse, status_code=status.HTTP_200_OK
)
async def get_workspace_by_id(
    workspace_id: uuid.UUID,
    services: Annotated[WorkspaceService, Depends(get_workspace_service)],
):
    return await services.get_workspace(workspace_id)


@router.patch(
    "/{workspace_id}", response_model=WorkspaceResponse, status_code=status.HTTP_200_OK
)
async def update_workspace(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    create_workspace_request: WorkspaceUpdateRequest,
    services: Annotated[WorkspaceService, Depends(get_workspace_service)],
):
    return await services.update_workspace(
        workspace_id, current_user, create_workspace_request
    )


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace_by_id(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[WorkspaceService, Depends(get_workspace_service)],
):
    return await services.delete_workspace(workspace_id, current_user)


@router.post(
    "/{workspace_id}/members",
    response_model=WorkspaceMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_workspace_member(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    add_member_request: WorkspaceAddMemberRequest,
    services: Annotated[WorkspaceService, Depends(get_workspace_service)],
):
    return await services.add_workspace_member(
        workspace_id, current_user, add_member_request
    )


@router.delete(
    "/{workspace_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_workspace_member(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[WorkspaceService, Depends(get_workspace_service)],
):
    await services.remove_workspace_member(workspace_id, user_id, current_user)


@router.post(
    "/{id}/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace_project(
    id: int,
    current_user: CurrentUser,
    create_project_request: ProjectCreateRequest,
    services: Annotated[WorkspaceService, Depends(get_workspace_service)],
):
    pass
