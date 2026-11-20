from pydantic import BaseModel, ConfigDict


class ProjectCreateRequest(BaseModel):
    pass


class ProjectResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )
