from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from api.schemas.task.task_schema_response import TaskSchemaResponse
from database.models.task.task_model import TaskModel


class TaskService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_task(
        self,
        taskSchema: TaskSchemaResponse,
    ) -> TaskModel:
        """Создать новую задачу"""

        task_id = str(uuid4())
        task = TaskModel(
            id=task_id,
            title=taskSchema.title,
            description=taskSchema.description,
            start_time=taskSchema.start_time,
            end_time=taskSchema.end_time,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.db_session.add(task)
        await self.db_session.commit()
        await self.db_session.refresh(task)

        return task

    async def get_task_by_id(self, task_id: str) -> Optional[TaskModel]:
        """Получить задачу по ID"""

        query = select(TaskModel).where(TaskModel.id == task_id)
        result = await self.db_session.execute(query)
        task = result.scalars().first()

        return task

    async def get_all_tasks(self) -> List[TaskModel]:
        """Получить все задачи"""

        query = select(TaskModel)
        result = await self.db_session.execute(query)
        tasks = result.scalars().all()

        return list(tasks)

    async def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Optional[TaskModel]:
        """Обновить задачу"""

        task = await self.get_task_by_id(task_id)
        if not task:
            return None

        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if start_time is not None:
            update_data["start_time"] = start_time
        if end_time is not None:
            update_data["end_time"] = end_time

        update_data["updated_at"] = datetime.now()

        query = update(TaskModel).where(
            TaskModel.id == task_id).values(**update_data)
        await self.db_session.execute(query)
        await self.db_session.commit()

        return await self.get_task_by_id(task_id)

    async def delete_task(self, task_id: str) -> bool:
        """Удалить задачу"""

        task = await self.get_task_by_id(task_id)
        if not task:
            return False

        query = delete(TaskModel).where(TaskModel.id == task_id)
        await self.db_session.execute(query)
        await self.db_session.commit()

        return True

    async def get_tasks_by_date_range(self, start_date: datetime, end_date: datetime) -> List[TaskModel]:
        """Получить задачи в заданном временном диапазоне"""

        query = select(TaskModel).where(
            TaskModel.start_time >= start_date,
            TaskModel.end_time <= end_date
        )
        result = await self.db_session.execute(query)
        tasks = result.scalars().all()

        return list(tasks)
