import uuid

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.core.enums import WorkspaceMemberRole
from taskhub.core.messages import ErrorMessage
from taskhub.exceptions import (
    AlreadyExistedException,
    NotFoundException,
    PermissionDeniedException,
)
from taskhub.exceptions.bad_request_ex import BadRequestException
from taskhub.models import User, Workspace, WorkspaceMember
from taskhub.repos import WorkspaceMemberRepository, WorkspaceRepository
from taskhub.schemas.workspace import (
    WorkspaceAddMemberRequest,
    WorkspaceCreateRequest,
    WorkspaceUpdateRequest,
)
from taskhub.services.user_service import UserService


class WorkspaceService:
    def __init__(self, db: AsyncSession, user_service: UserService):
        self.db = db
        self.workspace_repository = WorkspaceRepository(db)
        self.workspace_member_repository = WorkspaceMemberRepository(db)
        self.user_service = user_service

    async def get_workspace(self, workspace_id: uuid.UUID) -> Workspace:
        workspace = await self.workspace_repository.get_by_id(workspace_id)
        if workspace is None:
            raise NotFoundException(
                find_by="id",
                value=workspace_id,
                message=ErrorMessage.WORKSPACE_NOT_FOUND,
            )
        return workspace

    async def _ensure_owner(self, user_id: uuid.UUID, workspace_id: uuid.UUID) -> None:
        member = await self.workspace_member_repository.get_by_id(
            (workspace_id, user_id)
        )
        if member is None or member.role != WorkspaceMemberRole.OWNER:
            raise PermissionDeniedException(
                message=ErrorMessage.WORKSPACE_OWNER_REQUIRED
            )

    async def create_new_workspace(
        self, current_user: User, create_request: WorkspaceCreateRequest
    ):
        workspace_dict = {
            "name": create_request.name,
            "owner_id": current_user.id,
        }

        try:
            workspace = await self.workspace_repository.create(workspace_dict)
            # Thêm người tạo vào danh sách thành viên
            await self._add_workspace_member(
                current_user.id, workspace.id, role=WorkspaceMemberRole.OWNER
            )
            await self.db.commit()
            await self.db.refresh(workspace)
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        return workspace

    async def update_workspace(
        self,
        workspace_id: uuid.UUID,
        current_user: User,
        update_request: WorkspaceUpdateRequest,
    ):
        # Chủ workspace mới được chỉnh sửa
        workspace = await self.get_workspace(workspace_id)
        await self._ensure_owner(user_id=current_user.id, workspace_id=workspace.id)

        update_dict = update_request.model_dump(exclude_unset=True, exclude_none=True)
        if not update_dict:
            return workspace

        workspace = await self.workspace_repository.update(workspace, update_dict)

        try:
            await self.db.commit()
            await self.db.refresh(workspace)
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        return workspace

    async def _add_workspace_member(
        self,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
        role: WorkspaceMemberRole,
    ) -> WorkspaceMember:
        workspace_member_dict = {
            "user_id": user_id,
            "workspace_id": workspace_id,
            "role": role,
        }
        return await self.workspace_member_repository.create(workspace_member_dict)

    async def add_workspace_member(
        self,
        workspace_id: uuid.UUID,
        current_user: User,
        add_member_request: WorkspaceAddMemberRequest,
    ):
        # Không thể thêm chủ workspace
        if add_member_request.role == WorkspaceMemberRole.OWNER:
            raise BadRequestException(message=ErrorMessage.CANNOT_ASSIGN_OWNER_ROLE)

        # Chủ workspace mới được thêm thành viên
        workspace = await self.get_workspace(workspace_id)
        await self._ensure_owner(user_id=current_user.id, workspace_id=workspace.id)

        target_user = await self.user_service.get_user(add_member_request.user_id)
        member_existed = await self.workspace_member_repository.get_by_id(
            (workspace.id, target_user.id)
        )

        if member_existed is not None:
            raise AlreadyExistedException(
                key=str(target_user.id),
                message=ErrorMessage.MEMBER_ALREADY_EXISTS,
            )

        try:
            workspace_member = await self._add_workspace_member(
                user_id=target_user.id,
                workspace_id=workspace.id,
                role=add_member_request.role,
            )
            await self.db.commit()
            await self.db.refresh(workspace_member)
        except IntegrityError:
            await self.db.rollback()
            raise AlreadyExistedException(
                key="user_id",
                value=target_user.id,
                message=ErrorMessage.MEMBER_ALREADY_EXISTS,
            )

        return workspace_member

    async def remove_workspace_member(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        current_user: User,
    ):
        # Chủ workspace mới được xóa thành viên
        workspace = await self.get_workspace(workspace_id)
        await self._ensure_owner(user_id=current_user.id, workspace_id=workspace.id)

        target_user = await self.user_service.get_user(user_id)
        member_existed = await self.workspace_member_repository.get_by_id(
            (workspace.id, target_user.id)
        )

        if member_existed is None:
            raise NotFoundException(
                find_by="id",
                value=target_user.id,
                message=ErrorMessage.WORKSPACE_MEMBER_NOT_FOUND,
            )

        await self.workspace_member_repository.delete(member_existed)

        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def delete_workspace(
        self,
        workspace_id: uuid.UUID,
        current_user: User,
    ):
        # Chỉ chủ sở hữu mới có quyền xóa
        workspace = await self.get_workspace(workspace_id)
        await self._ensure_owner(user_id=current_user.id, workspace_id=workspace.id)
        await self.workspace_repository.delete(workspace)
        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise
