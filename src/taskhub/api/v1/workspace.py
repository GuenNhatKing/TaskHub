from typing import Annotated

from fastapi import APIRouter, Depends, status

from taskhub.core.dependencies import CurrentUser, get_workspace_service
from taskhub.schemas.project import ProjectCreateRequest, ProjectResponse
from taskhub.schemas.workspace import (
    WorkspaceAddMemberRequest,
    WorkspaceCreateRequest,
    WorkspaceMemberResponse,
    WorkspaceResponse,
)
from taskhub.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    current_user: CurrentUser,
    create_workspace_request: WorkspaceCreateRequest,
    services: Annotated[WorkspaceService, Depends(get_workspace_service)],
):
    pass


@router.get("/{id}", response_model=WorkspaceResponse, status_code=status.HTTP_200_OK)
async def get_workspace_by_id(
    id: int,
    current_user: CurrentUser,
    services: Annotated[WorkspaceService, Depends(get_workspace_service)],
):
    pass


@router.post(
    "/{id}/members",
    response_model=WorkspaceMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_workspace_member(
    id: int,
    current_user: CurrentUser,
    add_member_request: WorkspaceAddMemberRequest,
    services: Annotated[WorkspaceService, Depends(get_workspace_service)],
):
    pass


@router.delete("/{id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_workspace_member(
    id: int,
    user_id: int,
    current_user: CurrentUser,
    services: Annotated[WorkspaceService, Depends(get_workspace_service)],
):
    pass


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
