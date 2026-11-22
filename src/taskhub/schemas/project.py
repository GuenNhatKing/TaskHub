import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from taskhub.core.enums import ProjectStatus
from taskhub.core.validators import ValidDescription, ValidProjectName


class ProjectCreateRequest(BaseModel):
    name: ValidProjectName
    description: ValidDescription | None = None


class ProjectUpdateRequest(BaseModel):
    name: ValidProjectName | None = None
    description: ValidDescription | None = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    description: str
    status: ProjectStatus
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
