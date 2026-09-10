"""Unit tests for input validation."""

import pytest
from pydantic import ValidationError

from app.models import TaskCreate, TaskUpdate


def test_task_title_must_have_at_least_three_characters() -> None:
    with pytest.raises(ValidationError):
        TaskCreate(title="CI")


def test_task_create_uses_empty_description_by_default() -> None:
    task = TaskCreate(title="Pipeline teszt")

    assert task.description == ""


def test_partial_update_accepts_only_completion_state() -> None:
    update = TaskUpdate(completed=True)

    assert update.model_dump(exclude_unset=True) == {"completed": True}
