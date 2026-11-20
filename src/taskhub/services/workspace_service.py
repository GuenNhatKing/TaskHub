from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.repos.workspace import WorkspaceRepository


class WorkspaceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.workspace_repository = WorkspaceRepository(db)
