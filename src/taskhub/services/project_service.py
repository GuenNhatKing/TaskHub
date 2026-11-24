import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.core.enums import ProjectStatus, WorkspaceMemberRole
from taskhub.core.messages import ErrorMessage
from taskhub.exceptions import (
    NotFoundException,
    PermissionDeniedException,
)
from taskhub.exceptions.bad_request_ex import BadRequestException
from taskhub.models import Project, User
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

    async def ensure_workspace_member(
        self, user_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> None:
        member = await self.workspace_member_repository.get_by_id(
            (workspace_id, user_id)
        )
        if member is None:
            raise PermissionDeniedException(
                message=ErrorMessage.WORKSPACE_MEMBER_NOT_FOUND
            )

    async def ensure_editor_or_owner(
        self, user_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> None:
        member = await self.workspace_member_repository.get_by_id(
            (workspace_id, user_id)
        )
        if member is None or member.role not in (
            WorkspaceMemberRole.OWNER,
            WorkspaceMemberRole.EDITOR,
        ):
            raise PermissionDeniedException(
                message=ErrorMessage.WORKSPACE_EDITOR_REQUIRED
            )

    def ensure_project_active(self, project: Project) -> None:
        if project.status == ProjectStatus.ARCHIVED:
            raise BadRequestException(message=ErrorMessage.PROJECT_ARCHIVED)

    async def create_project(
        self,
        workspace_id: uuid.UUID,
        current_user: User,
        create_request: ProjectCreateRequest,
    ) -> Project:
        workspace = await self.workspace_service.get_workspace(workspace_id)
        await self.ensure_editor_or_owner(
            user_id=current_user.id, workspace_id=workspace.id
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
        except Exception:
            await self.db.rollback()
            raise

        return project

    async def get_workspace_projects(
        self,
        workspace_id: uuid.UUID,
        current_user: User,
        status: ProjectStatus | None = None,
    ) -> list[Project]:
        workspace = await self.workspace_service.get_workspace(workspace_id)
        # Chỉ thành viên của workspace mới được xem danh sách project
        await self.ensure_workspace_member(
            user_id=current_user.id, workspace_id=workspace.id
        )

        return await self.project_repository.get_by_workspace_id(workspace.id, status)

    async def get_project_detail(
        self,
        project_id: uuid.UUID,
        current_user: User,
    ) -> Project:
        project = await self.get_project(project_id)
        await self.ensure_workspace_member(
            user_id=current_user.id, workspace_id=project.workspace_id
        )
        return project

    async def update_project(
        self,
        project_id: uuid.UUID,
        current_user: User,
        update_request: ProjectUpdateRequest,
    ) -> Project:
        project = await self.get_project(project_id)
        await self.ensure_editor_or_owner(
            user_id=current_user.id, workspace_id=project.workspace_id
        )
        # Không cho chỉnh sửa thông tin nếu project đang ở trạng thái ARCHIVED
        self.ensure_project_active(project)

        update_dict = update_request.model_dump(exclude_unset=True, exclude_none=True)
        if not update_dict:
            return project

        project = await self.project_repository.update(project, update_dict)

        try:
            await self.db.commit()
            await self.db.refresh(project)
        except Exception:
            await self.db.rollback()
            raise

        return project

    async def archive_project(
        self,
        project_id: uuid.UUID,
        current_user: User,
    ) -> Project:
        project = await self.get_project(project_id)
        await self.ensure_editor_or_owner(
            user_id=current_user.id, workspace_id=project.workspace_id
        )

        if project.status == ProjectStatus.ARCHIVED:
            return project

        project = await self.project_repository.update(
            project, {"status": ProjectStatus.ARCHIVED}
        )

        try:
            await self.db.commit()
            await self.db.refresh(project)
        except Exception:
            await self.db.rollback()
            raise

        return project

    async def unarchive_project(
        self,
        project_id: uuid.UUID,
        current_user: User,
    ) -> Project:
        project = await self.get_project(project_id)
        await self.ensure_editor_or_owner(
            user_id=current_user.id, workspace_id=project.workspace_id
        )

        if project.status == ProjectStatus.ACTIVE:
            return project

        project = await self.project_repository.update(
            project, {"status": ProjectStatus.ACTIVE}
        )

        try:
            await self.db.commit()
            await self.db.refresh(project)
        except Exception:
            await self.db.rollback()
            raise

        return project

    async def delete_project(
        self,
        project_id: uuid.UUID,
        current_user: User,
    ) -> None:
        project = await self.get_project(project_id)
        await self.ensure_editor_or_owner(
            user_id=current_user.id, workspace_id=project.workspace_id
        )

        await self.project_repository.delete(project)

        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise
