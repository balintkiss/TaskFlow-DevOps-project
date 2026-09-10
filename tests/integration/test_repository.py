"""Integration tests exercise the repository against a real SQLite file."""

from pathlib import Path

import pytest

from app import repository
from app.config import get_settings


@pytest.fixture(autouse=True)
def isolated_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "repository.db"))
    get_settings.cache_clear()
    repository.initialize_database()


def test_task_lifecycle() -> None:
    created = repository.create_task("Integrációs teszt", "SQLite használatával")
    updated = repository.update_task(created["id"], {"completed": True})

    assert updated is not None
    assert updated["completed"] is True
    assert repository.task_stats() == {"total": 1, "completed": 1, "pending": 0}
    assert repository.delete_task(created["id"]) is True
    assert repository.get_task(created["id"]) is None


def test_filtering_completed_tasks() -> None:
    first = repository.create_task("Első feladat", "")
    repository.create_task("Második feladat", "")
    repository.update_task(first["id"], {"completed": True})

    completed = repository.list_tasks(completed=True)

    assert [task["title"] for task in completed] == ["Első feladat"]
