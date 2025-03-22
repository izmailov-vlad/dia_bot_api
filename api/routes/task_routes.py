from fastapi import APIRouter, Depends
from typing import List
import logging

from api.repository.task_repository import TaskRepository, get_task_repository
from api.schemas.task.task_schema_create import TaskSchemaCreate
from api.schemas.task.task_schema_response import TaskSchemaResponse
from api.schemas.task.task_schema_update import TaskSchemaUpdate

from api.middleware.auth_middleware import get_current_user
from database.models.user.user_model import UserModel

# Настраиваем логгер для этого модуля
logger = logging.getLogger(__name__)

router = APIRouter(tags=["tasks"])


@router.post("/tasks", response_model=TaskSchemaResponse)
async def create_task(
    task: TaskSchemaCreate,
    current_user: UserModel = Depends(get_current_user),
    task_repository: TaskRepository = Depends(get_task_repository)
):
    """Создание новой задачи"""
    try:
        return await task_repository.create_task(task, current_user.id)
    except Exception as e:
        raise


@router.get("/tasks/{task_id}", response_model=TaskSchemaResponse)
async def get_task(task_id: str, task_repository: TaskRepository = Depends(get_task_repository)):
    """Получение задачи по ID"""
    return await task_repository.get_task_by_id(task_id)


@router.get("/tasks", response_model=List[TaskSchemaResponse])
async def get_tasks(
    current_user: UserModel = Depends(get_current_user),
    task_repository: TaskRepository = Depends(get_task_repository),
):
    """Получение всех задач"""
    return await task_repository.get_all_tasks(current_user.id)


@router.put("/tasks/{task_id}", response_model=TaskSchemaResponse)
async def update_task(
    task_id: str,
    task: TaskSchemaUpdate,
    current_user: UserModel = Depends(get_current_user),
    task_repository: TaskRepository = Depends(get_task_repository)
):
    """Обновление задачи"""
    return await task_repository.update_task(task_id=task_id, user_id=current_user.id, task=task)


@router.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(
    task_id: str,
    current_user: UserModel = Depends(get_current_user),
    task_repository: TaskRepository = Depends(get_task_repository)
):
    """Удаление задачи"""
    success = await task_repository.delete_task(task_id, current_user.id)
    return {'success': success}
