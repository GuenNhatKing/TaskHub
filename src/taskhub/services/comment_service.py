import uuid

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.core.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from taskhub.core.enums import WorkspaceMemberRole
from taskhub.core.messages import ErrorMessage
from taskhub.exceptions import NotFoundException, PermissionDeniedException
from taskhub.models import Comment, User
from taskhub.repos.base import Page
from taskhub.repos.comment import CommentRepository
from taskhub.schemas.comment import CommentCreateRequest, CommentUpdateRequest
from taskhub.services.project_service import ProjectService
from taskhub.services.task_service import TaskService
from taskhub.services.workspace_service import WorkspaceService


class CommentService:
    def __init__(
        self,
        db: AsyncSession,
        project_service: ProjectService,
        task_service: TaskService,
        workspace_service: WorkspaceService,
    ):
        self.db = db
        self.comment_repository = CommentRepository(db)
        self.project_service = project_service
        self.task_service = task_service
        self.workspace_service = workspace_service

    async def get_comment(self, comment_id: uuid.UUID) -> Comment:
        comment = await self.comment_repository.get_by_id(comment_id)
        if comment is None:
            raise NotFoundException(
                find_by="id",
                value=comment_id,
                message=ErrorMessage.COMMENT_NOT_FOUND,
            )
        return comment

    async def create_comment(
        self,
        task_id: uuid.UUID,
        current_user: User,
        create_request: CommentCreateRequest,
    ) -> Comment:
        task = await self.task_service.get_task(task_id)
        project = await self.project_service.get_project(task.project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
            allowed_roles=[WorkspaceMemberRole.OWNER, WorkspaceMemberRole.EDITOR],
            error_message=ErrorMessage.WORKSPACE_EDITOR_REQUIRED,
        )
        self.project_service.ensure_project_active(project)

        comment_dict = {
            "task_id": task.id,
            "author_id": current_user.id,
            "content": create_request.content,
        }

        try:
            comment = await self.comment_repository.create(comment_dict)
            await self.db.commit()
            await self.db.refresh(comment)
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        return comment

    async def get_task_comments(
        self,
        task_id: uuid.UUID,
        current_user: User,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Page[Comment]:
        task = await self.task_service.get_task(task_id)
        project = await self.project_service.get_project(task.project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
        )

        return await self.comment_repository.get_by_task_id(
            task_id=task.id,
            page=page,
            page_size=page_size,
        )

    async def update_comment(
        self,
        comment_id: uuid.UUID,
        current_user: User,
        update_request: CommentUpdateRequest,
    ) -> Comment:
        comment = await self.get_comment(comment_id)
        task = await self.task_service.get_task(comment.task_id)
        project = await self.project_service.get_project(task.project_id)

        await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
        )

        # Chỉ chính tác giả bình luận mới được phép chỉnh sửa
        if comment.author_id != current_user.id:
            raise PermissionDeniedException(
                message=ErrorMessage.COMMENT_EDIT_PERMISSION_DENIED
            )

        self.project_service.ensure_project_active(project)

        update_dict = update_request.model_dump(exclude_unset=True)
        if not update_dict:
            return comment

        comment = await self.comment_repository.update(comment, update_dict)

        try:
            await self.db.commit()
            await self.db.refresh(comment)
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        return comment

    async def delete_comment(
        self,
        comment_id: uuid.UUID,
        current_user: User,
    ) -> None:
        comment = await self.get_comment(comment_id)
        task = await self.task_service.get_task(comment.task_id)
        project = await self.project_service.get_project(task.project_id)

        member = await self.workspace_service.ensure_workspace_role(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
        )
        self.project_service.ensure_project_active(project)

        # Chỉ tác giả comment hoặc chủ workspace mới có quyền xóa
        if (
            comment.author_id != current_user.id
            and member.role != WorkspaceMemberRole.OWNER
        ):
            raise PermissionDeniedException(
                message=ErrorMessage.COMMENT_DELETE_PERMISSION_DENIED
            )

        await self.comment_repository.delete(comment)

        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise
