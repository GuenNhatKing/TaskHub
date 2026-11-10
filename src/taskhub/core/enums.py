from enum import Enum


class LabelColor(str, Enum):
    RED = "#EF4444"
    ORANGE = "#F97316"
    YELLOW = "#EAB308"
    GREEN = "#22C55E"
    BLUE = "#3B82F6"
    PURPLE = "#A855F7"
    PINK = "#EC4899"
    TEAL = "#14B8A6"
    BROWN = "#78350F"
    GRAY = "#6B7280"


class ProjectStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    IN_REVIEW = "IN_REVIEW"
    DONE = "DONE"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class ROLE(str, Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class WorkspaceMemberRole(str, Enum):
    OWNER = "OWNER"
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"
