from pydantic import BaseModel
from datetime import datetime
from typing import get_type_hints, get_args, get_origin, Union, Optional


def get_schema_fields(schema_class: type[BaseModel]) -> str:
    """
    Получает простое описание полей Pydantic схемы в формате:
    field_name: python_type
    """
    fields = []
    hints = get_type_hints(schema_class)

    for field_name, field_type in hints.items():
        # Пропускаем служебные поля
        if field_name == "model_config":
            continue

        # Определяем базовый тип
        if get_origin(field_type) in (Union, Optional):
            args = get_args(field_type)
            # Убираем NoneType из Union
            types = [t for t in args if t != type(None)]
            if len(types) == 1:
                type_name = _get_type_name(types[0])
                type_name = f"{type_name} | null"
            else:
                type_name = " | ".join(_get_type_name(t) for t in types)
        else:
            type_name = _get_type_name(field_type)

        fields.append(f"{field_name}: {type_name}")

    return f"{schema_class.__name__}:\n" + "\n".join(fields)


def _get_type_name(type_):
    """Преобразует тип Python в строковое представление"""
    if type_ == str:
        return "str"
    elif type_ == int:
        return "int"
    elif type_ == datetime:
        return "datetime"
    elif type_ == bool:
        return "bool"
    elif type_ == float:
        return "float"
    elif hasattr(type_, "__name__"):
        return type_.__name__
    return str(type_)
