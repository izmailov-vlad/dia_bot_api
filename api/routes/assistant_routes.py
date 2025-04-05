from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Union

from api.middleware.auth_middleware import get_current_user
from api.repository.agent_manager_repository import AgentManagerRepository, get_agent_manager_repository
from api.repository.task_repository import TaskRepository, get_task_repository
from api.schemas.schedule.edited_schedule_schema import EditedScheduleSchema
from database.models.user.user_model import UserModel
from api.service.schedule.schedule_service import ScheduleService, get_schedule_service
from api.service.intent_service.intent_service import IntentService, get_intent_service

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/request")
async def request_assistant(
    message: str,
    current_user: UserModel = Depends(get_current_user),
    task_repository: TaskRepository = Depends(
        get_task_repository,
    )
) -> Union[str, EditedScheduleSchema]:
    """
    Обработка сообщения пользователя через ассистента

    Args:
        message: Сообщение пользователя
        current_user: Текущий пользователь
        schedule_service: Сервис для работы с расписанием
        intent_service: Сервис для определения намерений

    Returns:
        Dict с ответом ассистента
    """
    try:
        tasks = await task_repository.search_by_query(message)
        return tasks

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке запроса: {str(e)}"
        )
