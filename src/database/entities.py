from pydantic import BaseModel, field_validator
from typing import Optional, Union
from src.enums.Task import TaskStatus
from datetime import datetime, timezone

class CreateTask(BaseModel):
    name: str
    description: Optional[str] = ''
    status: TaskStatus = TaskStatus.PENDING

class TaskResponce(BaseModel):
    id: int
    name: str
    description: str
    status: TaskStatus
    created_at: datetime

    @field_validator('created_at')
    def parse_created_at(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return value

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
