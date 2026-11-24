import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from taskhub.core.enums import WorkspaceMemberRole
from taskhub.core.validators import ValidWorkspaceName


class WorkspaceCreateRequest(BaseModel):
    name: ValidWorkspaceName


class WorkspaceUpdateRequest(BaseModel):
    name: ValidWorkspaceName | None = None


class WorkspaceAddMemberRequest(BaseModel):
    user_id: uuid.UUID
    role: WorkspaceMemberRole


class WorkspaceResponse(BaseModel):
    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(
        from_attributes=True,
    )


class WorkspaceMemberResponse(BaseModel):
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    role: WorkspaceMemberRole
    model_config = ConfigDict(
        from_attributes=True,
    )
