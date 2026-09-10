"""Request and response models for the REST API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100, examples=["CI pipeline elkészítése"])
    description: str = Field(default="", max_length=500)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    completed: bool | None = None


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime


class TaskStats(BaseModel):
    total: int
    completed: int
    pending: int


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
