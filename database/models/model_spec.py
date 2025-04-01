from sqlalchemy import inspect


def get_model_fields(model_class) -> str:
    """
    Получает простое описание полей модели в формате:
    field_name: python_type
    """
    inspector = inspect(model_class)
    fields = []

    for column in inspector.columns:
        type_name = str(column.type)

        # Добавляем | null для nullable полей
        if column.nullable:
            type_name = f"{type_name} | null"

        fields.append(f"{column.name}: {type_name}")

    return "TaskModel:\n" + "\n".join(fields)
