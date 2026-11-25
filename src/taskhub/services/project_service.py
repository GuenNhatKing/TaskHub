import uuid

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.core.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from taskhub.core.enums import ProjectStatus, WorkspaceMemberRole
from taskhub.core.messages import ErrorMessage
from taskhub.exceptions import (
    NotFoundException,
)
from taskhub.exceptions.bad_request_ex import BadRequestException
from taskhub.models import Project, User
from taskhub.repos.base import Page
from taskhub.repos.project import ProjectRepository
from taskhub.repos.workspace_member import WorkspaceMemberRepository
from taskhub.schemas.project import ProjectCreateRequest, ProjectUpdateRequest
from taskhub.services.workspace_service import WorkspaceService


class ProjectService:
    def __init__(self, db: AsyncSession, workspace_service: WorkspaceService):
        self.db = db
        self.project_repository = ProjectRepository(db)
        self.workspace_member_repository = WorkspaceMemberRepository(db)
        self.workspace_service = workspace_service

    async def get_project(self, project_id: uuid.UUID) -> Project:
        project = await self.project_repository.get_by_id(project_id)
        if project is None:
            raise NotFoundException(
                find_by="id",
                value=project_id,
                message=ErrorMessage.PROJECT_NOT_FOUND,
            )
        return project

    def ensure_project_active(self, project: Project) -> None:
        if project.status == ProjectStatus.ARCHIVED:
            raise BadRequestException(message=ErrorMessage.PROJECT_ARCHIVED)

    async def create_project(
        self,
        workspace_id: uuid.UUID,
        current_user: User,
        create_request: ProjectCreateRequest,
    ) -> Project:
        workspace = await self.workspace_service.get_workspace(
            workspace_id, current_user
        )

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=workspace.id,
            allowed_roles=[WorkspaceMemberRole.OWNER, WorkspaceMemberRole.EDITOR],
            error_message=ErrorMessage.WORKSPACE_EDITOR_REQUIRED,
        )

        project_dict = {
            "workspace_id": workspace.id,
            "name": create_request.name,
            "description": create_request.description,
        }

        try:
            project = await self.project_repository.create(project_dict)
            await self.db.commit()
            await self.db.refresh(project)
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        return project

    async def get_workspace_projects(
        self,
        workspace_id: uuid.UUID,
        current_user: User,
        status: ProjectStatus | None = None,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Page[Project]:
        # get_workspace đã kiểm tra luôn quyền thành viên của current_user
        workspace = await self.workspace_service.get_workspace(
            workspace_id, current_user
        )

        return await self.project_repository.get_by_workspace_id(
            workspace_id=workspace.id,
            status=status,
            page=page,
            page_size=page_size,
        )

    async def get_project_detail(
        self,
        project_id: uuid.UUID,
        current_user: User,
    ) -> Project:
        project = await self.get_project(project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
        )
        return project

    async def update_project(
        self,
        project_id: uuid.UUID,
        current_user: User,
        update_request: ProjectUpdateRequest,
    ) -> Project:
        project = await self.get_project(project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
            allowed_roles=[WorkspaceMemberRole.OWNER, WorkspaceMemberRole.EDITOR],
            error_message=ErrorMessage.WORKSPACE_EDITOR_REQUIRED,
        )

        # Không cho chỉnh sửa thông tin nếu project đang ở trạng thái ARCHIVED
        self.ensure_project_active(project)

        update_dict = update_request.model_dump(exclude_unset=True)
        if not update_dict:
            return project

        project = await self.project_repository.update(project, update_dict)

        try:
            await self.db.commit()
            await self.db.refresh(project)
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        return project

    async def archive_project(
        self,
        project_id: uuid.UUID,
        current_user: User,
    ) -> Project:
        project = await self.get_project(project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
            allowed_roles=[WorkspaceMemberRole.OWNER, WorkspaceMemberRole.EDITOR],
            error_message=ErrorMessage.WORKSPACE_EDITOR_REQUIRED,
        )

        if project.status == ProjectStatus.ARCHIVED:
            return project

        project = await self.project_repository.update(
            project, {"status": ProjectStatus.ARCHIVED}
        )

        try:
            await self.db.commit()
            await self.db.refresh(project)
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        return project

    async def unarchive_project(
        self,
        project_id: uuid.UUID,
        current_user: User,
    ) -> Project:
        project = await self.get_project(project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
            allowed_roles=[WorkspaceMemberRole.OWNER, WorkspaceMemberRole.EDITOR],
            error_message=ErrorMessage.WORKSPACE_EDITOR_REQUIRED,
        )

        if project.status == ProjectStatus.ACTIVE:
            return project

        project = await self.project_repository.update(
            project, {"status": ProjectStatus.ACTIVE}
        )

        try:
            await self.db.commit()
            await self.db.refresh(project)
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        return project

    async def delete_project(
        self,
        project_id: uuid.UUID,
        current_user: User,
    ) -> None:
        project = await self.get_project(project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
            allowed_roles=[WorkspaceMemberRole.OWNER, WorkspaceMemberRole.EDITOR],
            error_message=ErrorMessage.WORKSPACE_EDITOR_REQUIRED,
        )

        await self.project_repository.delete(project)

        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise
