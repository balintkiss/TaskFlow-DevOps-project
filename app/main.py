"""FastAPI entrypoint and HTTP routes."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import FileResponse, Response

from app import __version__, repository
from app.config import get_settings
from app.models import HealthResponse, Task, TaskCreate, TaskStats, TaskUpdate


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    repository.initialize_database()
    yield


app = FastAPI(
    title="TaskFlow API",
    description="Egyszerű feladatkezelő API tesztautomatizálási és DevOps demóhoz.",
    version=__version__,
    lifespan=lifespan,
)


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
def health() -> HealthResponse:
    return HealthResponse(status="healthy", service=get_settings().app_name, version=__version__)


@app.get("/api/tasks", response_model=list[Task], tags=["Tasks"])
def read_tasks(completed: bool | None = Query(default=None)) -> list[dict]:
    return repository.list_tasks(completed)


@app.get("/api/tasks/{task_id}", response_model=Task, tags=["Tasks"])
def read_task(task_id: int) -> dict:
    task = repository.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="A feladat nem található")
    return task


@app.post("/api/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def add_task(payload: TaskCreate) -> dict:
    return repository.create_task(payload.title, payload.description)


@app.patch("/api/tasks/{task_id}", response_model=Task, tags=["Tasks"])
def edit_task(task_id: int, payload: TaskUpdate) -> dict:
    task = repository.update_task(task_id, payload.model_dump(exclude_unset=True))
    if task is None:
        raise HTTPException(status_code=404, detail="A feladat nem található")
    return task


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
def remove_task(task_id: int) -> Response:
    if not repository.delete_task(task_id):
        raise HTTPException(status_code=404, detail="A feladat nem található")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/stats", response_model=TaskStats, tags=["Monitoring"])
def stats() -> dict[str, int]:
    return repository.task_stats()
