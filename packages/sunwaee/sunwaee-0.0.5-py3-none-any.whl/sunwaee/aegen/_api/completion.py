# standard
import json

# third party
import fastapi
import pydantic
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# custom
from sunwaee.aegen import async_completion
from sunwaee.aegen._api._router import aegen_router
from sunwaee.aegen.message import Message
from sunwaee.aegen.response import Response
from sunwaee.aegen.tool import Tool


class CompletionRequest(pydantic.BaseModel):
    agent: str
    messages: list[Message]
    tools: list[Tool] | None
    streaming: bool = False


@aegen_router.post("/completion", response_model=Response)
async def llm_completion(
    req: CompletionRequest,
    credentials: HTTPAuthorizationCredentials = fastapi.Depends(
        HTTPBearer(auto_error=True)
    ),
):
    """All models, one response format."""

    # NOTE no api_key -> 403
    api_key = credentials.credentials

    agent = req.agent
    messages = [m.to_dict() for m in req.messages]
    tools = [t.model_dump() for t in req.tools] if req.tools else None
    streaming = req.streaming

    if streaming:

        async def event_generator():
            async for chunk in async_completion(
                agent=agent,
                api_key=api_key,
                messages=messages,
                tools=tools,
                streaming=True,
            ):
                yield json.dumps(chunk) + "\n"

        return StreamingResponse(event_generator(), media_type="application/json")

    else:

        async for chunk in async_completion(
            agent=agent,
            api_key=api_key,
            messages=messages,
            tools=tools,
            streaming=False,
        ):
            return chunk
