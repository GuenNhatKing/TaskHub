import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from taskhub.core.validators import ValidCommentContent
from taskhub.schemas.base import BaseRequest


class CommentCreateRequest(BaseRequest):
    content: ValidCommentContent


class CommentUpdateRequest(BaseRequest):
    content: ValidCommentContent | None = None


class CommentResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    author_id: uuid.UUID
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentListResponse(BaseModel):
    items: list[CommentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
