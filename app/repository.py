"""Small SQLite repository kept separate so it can be tested in isolation."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from app.config import get_settings


def _database_path() -> str:
    return get_settings().database_path


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    database_path = _database_path()
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    database = sqlite3.connect(database_path)
    database.row_factory = sqlite3.Row
    try:
        yield database
        database.commit()
    finally:
        database.close()


def initialize_database() -> None:
    with connection() as database:
        database.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


def list_tasks(completed: bool | None = None) -> list[dict]:
    query = "SELECT * FROM tasks"
    parameters: tuple[object, ...] = ()
    if completed is not None:
        query += " WHERE completed = ?"
        parameters = (int(completed),)
    query += " ORDER BY id DESC"
    with connection() as database:
        rows = database.execute(query, parameters).fetchall()
    return [_to_dict(row) for row in rows]


def get_task(task_id: int) -> dict | None:
    with connection() as database:
        row = database.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return _to_dict(row) if row else None


def create_task(title: str, description: str) -> dict:
    now = datetime.now(UTC).isoformat()
    with connection() as database:
        cursor = database.execute(
            "INSERT INTO tasks (title, description, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (title, description, now, now),
        )
        task_id = cursor.lastrowid
    task = get_task(int(task_id))
    assert task is not None
    return task


def update_task(task_id: int, changes: dict) -> dict | None:
    allowed = {key: value for key, value in changes.items() if value is not None}
    if not allowed:
        return get_task(task_id)
    if "completed" in allowed:
        allowed["completed"] = int(allowed["completed"])
    allowed["updated_at"] = datetime.now(UTC).isoformat()
    assignments = ", ".join(f"{column} = ?" for column in allowed)
    values = (*allowed.values(), task_id)
    with connection() as database:
        cursor = database.execute(f"UPDATE tasks SET {assignments} WHERE id = ?", values)
        if cursor.rowcount == 0:
            return None
    return get_task(task_id)


def delete_task(task_id: int) -> bool:
    with connection() as database:
        cursor = database.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return cursor.rowcount > 0


def task_stats() -> dict[str, int]:
    with connection() as database:
        row = database.execute(
            "SELECT COUNT(*) AS total, COALESCE(SUM(completed), 0) AS completed FROM tasks"
        ).fetchone()
    total = int(row["total"])
    completed = int(row["completed"])
    return {"total": total, "completed": completed, "pending": total - completed}


def _to_dict(row: sqlite3.Row) -> dict:
    task = dict(row)
    task["completed"] = bool(task["completed"])
    return task
