import uuid

from pydantic import BaseModel, ConfigDict

from taskhub.core.enums import LabelColor
from taskhub.core.validators import NotNull, ValidLabelName
from taskhub.schemas.base import BaseRequest


class LabelCreateRequest(BaseRequest):
    name: ValidLabelName
    color: LabelColor = LabelColor.BLUE


class LabelUpdateRequest(BaseRequest):
    name: NotNull[ValidLabelName | None] = None
    color: NotNull[LabelColor | None] = None


class TaskLabelAssignRequest(BaseRequest):
    label_id: uuid.UUID


class LabelResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    color: LabelColor

    model_config = ConfigDict(from_attributes=True)
