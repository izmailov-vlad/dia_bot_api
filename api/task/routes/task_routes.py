from fastapi import APIRouter, Depends, Query
from typing import Annotated, List
import logging
from datetime import datetime

from api.task.repository.task_repository import TaskRepository, get_task_repository
from api.task.schemas.task.task_response_schema import TaskResponseSchema
from api.task.schemas.task.task_create_schema import TaskCreateSchema
from api.task.schemas.task.task_update_schema import TaskUpdateSchema
from api.task.schemas.task.task_list_response_schema import TasksResponseSchema
from api.auth.middleware.auth_middleware import get_current_user
from database.models.user.user_model import UserModel

# Настраиваем логгер для этого модуля
logger = logging.getLogger(__name__)

router = APIRouter(tags=["tasks"])


@router.post("/tasks", response_model=TaskResponseSchema)
async def create_task(
    task: TaskCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    task_repository: TaskRepository = Depends(get_task_repository)
):
    """Создание новой задачи"""
    try:
        return await task_repository.create_task(task, current_user.id)
    except Exception as e:
        raise


@router.get("/tasks/{task_id}", response_model=TaskResponseSchema)
async def get_task(
    task_id: str,
    task_repository: TaskRepository = Depends(get_task_repository),
    current_user: UserModel = Depends(get_current_user)
):
    """Получение задачи по ID"""
    return await task_repository.get_task_by_id(task_id, current_user.id)


@router.get("/tasks", response_model=List[TaskResponseSchema])
async def get_tasks(
    current_user: UserModel = Depends(get_current_user),
    task_repository: TaskRepository = Depends(get_task_repository),
):
    """Получение всех задач"""
    return await task_repository.get_all_tasks(current_user.id)


@router.put("/tasks/{task_id}", response_model=TaskResponseSchema)
async def update_task(
    task_id: str,
    task: TaskUpdateSchema,
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


@router.get("/tasks/by-date/", response_model=TasksResponseSchema)
async def get_tasks_by_date(
    date: datetime = Query(...),
    current_user: UserModel = Depends(get_current_user),
    task_repository: TaskRepository = Depends(get_task_repository)
):
    """Получение задач на конкретный день"""
    tasks = await task_repository.get_tasks_by_date(date, current_user.id)
    return TasksResponseSchema(tasks=tasks)
