from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


def _clean_title(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    v = v.strip()
    if not v:
        raise ValueError("Title is required and cannot be blank")
    if len(v) > 200:
        raise ValueError("Title cannot exceed 200 characters")
    return v


def _clean_tags(v: Optional[list[str]]) -> Optional[list[str]]:
    if v is None:
        return v
    cleaned: list[str] = []
    seen: set[str] = set()
    for tag in v:
        t = tag.strip()
        if not t:
            raise ValueError("Tags cannot be blank")
        if len(t) > 20:
            raise ValueError("Each tag must be 20 characters or fewer")
        key = t.lower()
        if key not in seen:
            seen.add(key)
            cleaned.append(t)
    if len(cleaned) > 5:
        raise ValueError("A task can have at most 5 tags")
    return cleaned


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    tags: list[str] = []

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        cleaned = _clean_title(v)
        if cleaned is None:
            raise ValueError("Title is required and cannot be blank")
        return cleaned

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        return _clean_tags(v) or []


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    tags: Optional[list[str]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        return _clean_title(v)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        return _clean_tags(v)


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime