import json
from api.schemas.task.task_schema_create import TaskSchemaCreate
from api.schemas.task.task_schema_response import TaskSchemaResponse
from api.service.gpt.gpt_service import GPTService
from api.service.task.task_service import TaskService
from api.service.smart_tag_service import SmartTagService


class GPTRepository:
    def __init__(
        self,
        gpt_service: GPTService,
        task_service: TaskService,
        smart_tag_service: SmartTagService,
    ):
        self.gpt_service = gpt_service
        self.task_service = task_service
        self.smart_tag_service = smart_tag_service

    async def request(self, request: str):
        response = await self.gpt_service.request(request)

        if (response.choices[0].message.tool_calls == None):
            return {"message": response.choices[0].message.content}

        for tool_call in response.choices[0].message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            result = await self._call_function(name, args)

        return result

    # [request] field is a string from args
    async def create_task_tool(self, request: str) -> TaskSchemaResponse:
        taskSchemaResponseGpt = await self.task_service.create_task_gpt(request)
        taskSchemaResponse = await self.task_service.create_task(
            task=TaskSchemaCreate(
                title=taskSchemaResponseGpt.title,
                start_time=taskSchemaResponseGpt.start_time,
                end_time=taskSchemaResponseGpt.end_time
            ),
        )
        return taskSchemaResponse

    async def _call_function(self, name, args):
        if name == "create_task_tool":
            task = self.create_task_tool(**args)

            return {"task": task}
