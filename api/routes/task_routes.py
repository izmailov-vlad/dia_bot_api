from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session
from database.database import get_db
from database.models.task.task_model import Task, TaskModel
from api.schemas.task.task_schema_create import TaskSchemaCreate
from api.schemas.task.task_schema_response import TaskSchemaResponse
from api.schemas.task.task_schema_update import TaskSchemaUpdate

router = APIRouter(tags=["tasks"])


@router.post("/tasks", response_model=TaskSchemaResponse)
async def create_task(task: TaskSchemaCreate, db: Session = Depends(get_db)):
    """Создание новой задачи"""
    db_task = TaskModel(
        id=str(uuid4()),
        title=task.title,
        description=task.description,
        start_time=task.start_time,
        end_time=task.end_time,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


@router.get("/tasks/{task_id}", response_model=TaskSchemaResponse)
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """Получение задачи по ID"""
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if db_task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return db_task


@router.get("/tasks", response_model=List[TaskSchemaResponse])
async def get_tasks(db: Session = Depends(get_db)):
    """Получение всех задач"""
    tasks = db.query(Task).all()
    return tasks


@router.put("/tasks/{task_id}", response_model=TaskSchemaResponse)
async def update_task(task_id: str, task: TaskSchemaUpdate, db: Session = Depends(get_db)):
    """Обновление задачи"""
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()

    if db_task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    update_data = task.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_task, key, value)

    db_task.updated_at = datetime.now()

    db.commit()
    db.refresh(db_task)

    return db_task


@router.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(task_id: str, db: Session = Depends(get_db)):
    """Удаление задачи"""
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()

    if db_task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    db.delete(db_task)
    db.commit()

    return {"message": "Задача успешно удалена"}


@router.get("/tasks/status/{status}", response_model=List[TaskSchemaResponse])
async def get_tasks_by_status(status: str, db: Session = Depends(get_db)):
    """Получение задач по статусу"""
    tasks = db.query(TaskModel).filter(TaskModel.status == status).all()
    return tasks


@router.get("/tasks/priority/{priority}", response_model=List[TaskSchemaResponse])
async def get_tasks_by_priority(priority: str, db: Session = Depends(get_db)):
    """Получение задач по приоритету"""
    tasks = db.query(TaskModel).filter(TaskModel.priority == priority).all()
    return tasks
