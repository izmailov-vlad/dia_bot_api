from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import json

from api.schemas.smart_tag.smart_tag_schema_create import SmartTagSchemaCreate

from api.schemas.smart_tag.smart_tag_schema_response import SmartTagSchemaResponse
from api.schemas.smart_tag.smart_tag_schema_update import SmartTagSchemaUpdate
from api.schemas.task.task_schema_response import TaskSchemaResponse
from api.service.smart_tag_service import SmartTagService
from api.service.task_service import TaskService
from dependencies import get_smart_tag_service, get_task_service


router = APIRouter(tags=["smart_tags"])


@router.post("/smart-tags", response_model=SmartTagSchemaResponse)
async def create_smart_tag(
    smart_tag: SmartTagSchemaCreate,
    tag_service: SmartTagService = Depends(get_smart_tag_service)
):
    """
    Создание нового умного тега
    """
    return tag_service.create_smart_tag(smart_tag)


@router.get("/smart-tags", response_model=List[SmartTagSchemaResponse])
async def get_smart_tags(tag_service: SmartTagService = Depends(get_smart_tag_service)):
    """
    Получение списка умных тегов
    """
    # TODO: Получить user_id из авторизации
    user_id = "1"
    tags = tag_service.get_all_smart_tags_by_user_id(user_id)

    return tags


@router.get("/smart-tags/{tag_id}", response_model=SmartTagSchemaResponse)
async def get_smart_tag(
    tag_id: str,
    tag_service: SmartTagService = Depends(get_smart_tag_service)
):
    """
    Получение умного тега по ID

    - **tag_id**: Идентификатор метки
    """
    tag = tag_service.get_smart_tag_by_id(tag_id)

    if tag is None:
        raise HTTPException(status_code=404, detail="Умная метка не найдена")

    return tag


@router.put("/smart-tags/{tag_id}", response_model=SmartTagSchemaResponse)
async def update_smart_tag(
    tag_id: str,
    tag: SmartTagSchemaUpdate,
    tag_service: SmartTagService = Depends(get_smart_tag_service)
):
    """
    Обновление умного тега

    - **tag_id**: Идентификатор тега
    - **tag**: Данные для обновления тега
    """
    # Преобразуем сложный объект query в JSON строку, если он передан
    update_data = tag.model_dump(exclude_unset=True)

    updated_tag = tag_service.update_smart_tag(tag_id, update_data)

    if updated_tag is None:
        raise HTTPException(status_code=404, detail="Умный тег не найден")

    return updated_tag


@router.delete("/smart-tags/{tag_id}")
async def delete_smart_tag(
    tag_id: str,
    tag_service: SmartTagService = Depends(get_smart_tag_service)
):
    """
    Удаление умного тега

    - **tag_id**: Идентификатор тега
    """
    success = tag_service.delete_smart_tag(tag_id)

    if not success:
        raise HTTPException(status_code=404, detail="Умный тег не найден")

    return {"message": "Умный тег успешно удален"}
