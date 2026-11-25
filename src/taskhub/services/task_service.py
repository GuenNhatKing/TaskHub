import uuid
from datetime import UTC, datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.core.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from taskhub.core.enums import Priority, TaskStatus, WorkspaceMemberRole
from taskhub.core.messages import ErrorMessage
from taskhub.exceptions import NotFoundException
from taskhub.exceptions.bad_request_ex import BadRequestException
from taskhub.models import Task, User
from taskhub.repos.base import Page
from taskhub.repos.task import TaskRepository
from taskhub.repos.workspace_member import WorkspaceMemberRepository
from taskhub.schemas.task import TaskCreateRequest, TaskUpdateRequest
from taskhub.services.project_service import ProjectService
from taskhub.services.workspace_service import WorkspaceService


class TaskService:
    def __init__(
        self,
        db: AsyncSession,
        project_service: ProjectService,
        workspace_service: WorkspaceService,
    ):
        self.db = db
        self.task_repository = TaskRepository(db)
        self.workspace_member_repository = WorkspaceMemberRepository(db)
        self.project_service = project_service
        self.workspace_service = workspace_service

    async def get_task(self, task_id: uuid.UUID) -> Task:
        task = await self.task_repository.get_by_id(task_id)
        if task is None:
            raise NotFoundException(
                find_by="id",
                value=task_id,
                message=ErrorMessage.TASK_NOT_FOUND,
            )
        return task

    def validate_due_date(self, due_date: datetime | None) -> None:
        if due_date is None:
            return

        now = datetime.now(UTC)

        if due_date <= now:
            raise BadRequestException(message=ErrorMessage.INVALID_DUE_DATE)

    async def validate_assignee_in_workspace(
        self,
        workspace_id: uuid.UUID,
        assignee_id: uuid.UUID | None,
    ) -> None:
        if assignee_id is None:
            return
        member = await self.workspace_member_repository.get_by_id(
            (workspace_id, assignee_id)
        )
        if member is None:
            raise BadRequestException(message=ErrorMessage.ASSIGNEE_NOT_IN_WORKSPACE)

    async def create_task(
        self,
        project_id: uuid.UUID,
        current_user: User,
        create_request: TaskCreateRequest,
    ) -> Task:
        project = await self.project_service.get_project(project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
            allowed_roles=[WorkspaceMemberRole.OWNER, WorkspaceMemberRole.EDITOR],
            error_message=ErrorMessage.WORKSPACE_EDITOR_REQUIRED,
        )
        self.project_service.ensure_project_active(project)
        self.validate_due_date(create_request.due_date)

        await self.validate_assignee_in_workspace(
            workspace_id=project.workspace_id,
            assignee_id=create_request.assignee_id,
        )

        task_dict = {
            "project_id": project.id,
            "assignee_id": create_request.assignee_id,
            "title": create_request.title,
            "description": create_request.description,
            "status": create_request.status,
            "priority": create_request.priority,
            "due_date": create_request.due_date,
            "created_by": current_user.id,
        }

        try:
            task = await self.task_repository.create(task_dict)
            await self.db.commit()
            await self.db.refresh(task)
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        return task

    async def get_project_tasks(
        self,
        project_id: uuid.UUID,
        current_user: User,
        status: TaskStatus | None = None,
        priority: Priority | None = None,
        assignee_id: uuid.UUID | None = None,
        search: str | None = None,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Page[Task]:
        project = await self.project_service.get_project(project_id)

        # Kiểm tra current_user là thành viên workspace
        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
        )

        return await self.task_repository.get_by_project_id(
            project_id=project.id,
            page=page,
            page_size=page_size,
            status=status,
            priority=priority,
            assignee_id=assignee_id,
            search=search,
        )

    async def get_task_detail(
        self,
        task_id: uuid.UUID,
        current_user: User,
    ) -> Task:
        task = await self.get_task(task_id)
        project = await self.project_service.get_project(task.project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
        )
        return task

    async def update_task(
        self,
        task_id: uuid.UUID,
        current_user: User,
        update_request: TaskUpdateRequest,
    ) -> Task:
        task = await self.get_task(task_id)
        project = await self.project_service.get_project(task.project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
            allowed_roles=[WorkspaceMemberRole.OWNER, WorkspaceMemberRole.EDITOR],
            error_message=ErrorMessage.WORKSPACE_EDITOR_REQUIRED,
        )
        self.project_service.ensure_project_active(project)

        # Có thể chấp nhận None -> ví dụ gỡ asignee
        update_dict = update_request.model_dump(exclude_unset=True)
        if not update_dict:
            return task

        if "due_date" in update_dict:
            self.validate_due_date(update_dict["due_date"])

        if "assignee_id" in update_dict:
            await self.validate_assignee_in_workspace(
                workspace_id=project.workspace_id,
                assignee_id=update_dict["assignee_id"],
            )

        task = await self.task_repository.update(task, update_dict)

        try:
            await self.db.commit()
            await self.db.refresh(task)
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        return task

    async def delete_task(
        self,
        task_id: uuid.UUID,
        current_user: User,
    ) -> None:
        task = await self.get_task(task_id)
        project = await self.project_service.get_project(task.project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
            allowed_roles=[WorkspaceMemberRole.OWNER, WorkspaceMemberRole.EDITOR],
            error_message=ErrorMessage.WORKSPACE_EDITOR_REQUIRED,
        )
        self.project_service.ensure_project_active(project)

        await self.task_repository.delete(task)

        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise
