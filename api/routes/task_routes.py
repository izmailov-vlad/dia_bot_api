from fastapi import APIRouter, Depends
from typing import List

from api.service.task.task_service import TaskService
from api.schemas.task.task_schema_create import TaskSchemaCreate
from api.schemas.task.task_schema_response import TaskSchemaResponse
from api.schemas.task.task_schema_update import TaskSchemaUpdate
from dependencies import get_task_service
from api.middleware.auth_middleware import get_current_user
from database.models.user.user_model import UserModel

router = APIRouter(tags=["tasks"])


@router.post("/tasks", response_model=TaskSchemaResponse)
def create_task(
    task: TaskSchemaCreate,
    current_user: UserModel = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Создание новой задачи"""
    # Здесь мы можем установить task.user_id = current_user.id
    return task_service.create_task(task)


@router.get("/tasks/{task_id}", response_model=TaskSchemaResponse)
async def get_task(task_id: str, task_service: TaskService = Depends(get_task_service)):
    """Получение задачи по ID"""
    return await task_service.get_task_by_id(task_id)


@router.get("/tasks", response_model=List[TaskSchemaResponse])
async def get_tasks(task_service: TaskService = Depends(get_task_service)):
    """Получение всех задач"""
    return await task_service.get_all_tasks()


@router.put("/tasks/{task_id}", response_model=TaskSchemaResponse)
async def update_task(task_id: str, task: TaskSchemaUpdate, task_service: TaskService = Depends(get_task_service)):
    """Обновление задачи"""
    return await task_service.update_task(task_id, task)


@router.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(task_id: str, task_service: TaskService = Depends(get_task_service)):
    """Удаление задачи"""
    return await task_service.delete_task(task_id)
