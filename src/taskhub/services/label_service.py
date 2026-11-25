import uuid

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.core.enums import WorkspaceMemberRole
from taskhub.core.messages import ErrorMessage
from taskhub.exceptions import AlreadyExistedException, NotFoundException
from taskhub.exceptions.bad_request_ex import BadRequestException
from taskhub.models import Label, User
from taskhub.repos.label import LabelRepository
from taskhub.repos.task_label import TaskLabelRepository
from taskhub.schemas.label import LabelCreateRequest, LabelUpdateRequest
from taskhub.services.project_service import ProjectService
from taskhub.services.task_service import TaskService
from taskhub.services.workspace_service import WorkspaceService


class LabelService:
    def __init__(
        self,
        db: AsyncSession,
        project_service: ProjectService,
        task_service: TaskService,
        workspace_service: WorkspaceService,
    ):
        self.db = db
        self.label_repository = LabelRepository(db)
        self.task_label_repository = TaskLabelRepository(db)
        self.project_service = project_service
        self.task_service = task_service
        self.workspace_service = workspace_service

    async def get_label(self, label_id: uuid.UUID) -> Label:
        label = await self.label_repository.get_by_id(label_id)
        if label is None:
            raise NotFoundException(
                find_by="id",
                value=label_id,
                message=ErrorMessage.LABEL_NOT_FOUND,
            )
        return label

    async def create_label(
        self,
        project_id: uuid.UUID,
        current_user: User,
        create_request: LabelCreateRequest,
    ) -> Label:
        project = await self.project_service.get_project(project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
            allowed_roles=[WorkspaceMemberRole.OWNER, WorkspaceMemberRole.EDITOR],
            error_message=ErrorMessage.WORKSPACE_EDITOR_REQUIRED,
        )
        self.project_service.ensure_project_active(project)

        # Không tạo label với name đã có trong project
        existed = await self.label_repository.get_by_project_and_name(
            project.id, create_request.name
        )
        if existed is not None:
            raise AlreadyExistedException(
                key="name",
                message=ErrorMessage.LABEL_EXISTED,
            )

        label_dict = {
            "project_id": project.id,
            "name": create_request.name,
            "color": create_request.color,
        }

        try:
            label = await self.label_repository.create(label_dict)
            await self.db.commit()
            await self.db.refresh(label)
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        return label

    async def get_project_labels(
        self,
        project_id: uuid.UUID,
        current_user: User,
    ) -> list[Label]:
        project = await self.project_service.get_project(project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
        )

        return await self.label_repository.get_by_project_id(project.id)

    async def update_label(
        self,
        label_id: uuid.UUID,
        current_user: User,
        update_request: LabelUpdateRequest,
    ) -> Label:
        label = await self.get_label(label_id)
        project = await self.project_service.get_project(label.project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
            allowed_roles=[WorkspaceMemberRole.OWNER, WorkspaceMemberRole.EDITOR],
            error_message=ErrorMessage.WORKSPACE_EDITOR_REQUIRED,
        )
        self.project_service.ensure_project_active(project)

        update_dict = update_request.model_dump(exclude_unset=True)
        if not update_dict:
            return label

        # Kiểm tra khi cập nhật name, đảm bảo name chưa có trong project
        if "name" in update_dict and update_dict["name"].lower() != label.name.lower():
            existed = await self.label_repository.get_by_project_and_name(
                project.id, update_dict["name"]
            )
            if existed is not None:
                raise AlreadyExistedException(
                    key="name",
                    message=ErrorMessage.LABEL_EXISTED,
                )

        label = await self.label_repository.update(label, update_dict)

        try:
            await self.db.commit()
            await self.db.refresh(label)
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        return label

    async def delete_label(
        self,
        label_id: uuid.UUID,
        current_user: User,
    ) -> None:
        label = await self.get_label(label_id)
        project = await self.project_service.get_project(label.project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
            allowed_roles=[WorkspaceMemberRole.OWNER, WorkspaceMemberRole.EDITOR],
            error_message=ErrorMessage.WORKSPACE_EDITOR_REQUIRED,
        )
        self.project_service.ensure_project_active(project)

        await self.label_repository.delete(label)

        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def assign_label_to_task(
        self,
        task_id: uuid.UUID,
        label_id: uuid.UUID,
        current_user: User,
    ) -> list[Label]:
        task = await self.task_service.get_task(task_id)
        project = await self.project_service.get_project(task.project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
            allowed_roles=[WorkspaceMemberRole.OWNER, WorkspaceMemberRole.EDITOR],
            error_message=ErrorMessage.WORKSPACE_EDITOR_REQUIRED,
        )
        self.project_service.ensure_project_active(project)

        label = await self.get_label(label_id)
        if label.project_id != task.project_id:
            raise BadRequestException(message=ErrorMessage.LABEL_NOT_IN_PROJECT)

        existed = await self.task_label_repository.get_by_id((task.id, label.id))
        if existed is not None:
            raise AlreadyExistedException(
                key="label_id",
                message=ErrorMessage.TASK_LABEL_ALREADY_EXISTS,
            )

        task_label_dict = {
            "task_id": task.id,
            "label_id": label.id,
        }

        try:
            await self.task_label_repository.create(task_label_dict)
            await self.db.commit()
            await self.db.refresh(task)
        except IntegrityError:
            await self.db.rollback()
            raise AlreadyExistedException(
                key="label_id",
                message=ErrorMessage.TASK_LABEL_ALREADY_EXISTS,
            )
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        return await self.label_repository.get_by_task_id(task.id)

    async def get_task_labels(
        self,
        task_id: uuid.UUID,
        current_user: User,
    ) -> list[Label]:
        task = await self.task_service.get_task(task_id)
        project = await self.project_service.get_project(task.project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
        )

        return await self.label_repository.get_by_task_id(task.id)

    async def remove_label_from_task(
        self,
        task_id: uuid.UUID,
        label_id: uuid.UUID,
        current_user: User,
    ) -> None:
        task = await self.task_service.get_task(task_id)
        project = await self.project_service.get_project(task.project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
            allowed_roles=[WorkspaceMemberRole.OWNER, WorkspaceMemberRole.EDITOR],
            error_message=ErrorMessage.WORKSPACE_EDITOR_REQUIRED,
        )
        self.project_service.ensure_project_active(project)

        task_label = await self.task_label_repository.get_by_id((task.id, label_id))
        if task_label is None:
            raise NotFoundException(
                find_by="label_id",
                value=label_id,
                message=ErrorMessage.TASK_LABEL_NOT_FOUND,
            )

        await self.task_label_repository.delete(task_label)

        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise
