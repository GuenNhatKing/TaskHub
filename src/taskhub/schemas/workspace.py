from pydantic import BaseModel, ConfigDict


class WorkspaceCreateRequest(BaseModel):
    pass


class WorkspaceAddMemberRequest(BaseModel):
    pass


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )


class WorkspaceMemberResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )
