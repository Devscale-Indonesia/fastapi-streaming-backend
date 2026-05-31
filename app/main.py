from agents import Agent, Runner
from agents.extensions.models.any_llm_model import AnyLLMModel
from agents.sandbox.entries.mounts.providers.base import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# from openai import AsyncOpenAI
from fastapi.routing import json
from openai.lib.azure import os
from openai.types.responses import (
    ResponseReasoningTextDeltaEvent,
    ResponseTextDeltaEvent,
)

load_dotenv()

app = FastAPI()

# client = AsyncOpenAI(
#     api_key=os.getenv("OPENAI_API_KEY"),
# )

model = AnyLLMModel(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="openrouter/z-ai/glm-5.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def sse(payload: dict):
    return f"data: {json.dumps(payload)}\n\n"


@app.post("/")
async def do_streaming(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    part = messages[0].get("parts")[0]
    user_message = part.get("text")

    agent = Agent("assistant", instructions="You are a helpful assistant.", model=model)

    async def generator():
        reasoning_id = f"reasoning_{uuid.uuid4().hex}"
        text_id = f"text_{uuid.uuid4().hex}"
        message_id = f"message_{uuid.uuid4().hex}"

        yield sse({"type": "start", "messageId": message_id})
        yield sse({"type": "start-step"})

        yield sse({"type": "reasoning-start", "id": reasoning_id})
        yield sse({"type": "text-start", "id": text_id})

        runner = Runner.run_streamed(agent, input=user_message)

        async for event in runner.stream_events():
            if event.type == "raw_response_event":
                if isinstance(event.data, ResponseTextDeltaEvent):
                    yield sse(
                        {"type": "text-delta", "id": text_id, "delta": event.data.delta}
                    )
                if isinstance(event.data, ResponseReasoningTextDeltaEvent):
                    yield sse(
                        {
                            "type": "reasoning-delta",
                            "id": reasoning_id,
                            "delta": event.data.delta,
                        }
                    )

        yield sse({"type": "reasoning-end", "id": reasoning_id})
        yield sse({"type": "text-end", "id": text_id})
        yield sse({"type": "finish-step"})
        yield sse({"type": "finish"})
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={"x-vercel-ai-ui-stream-event": "v1", "cache-control": "no-cache"},
    )


# @app.post("/")
# async def do_streaming(request: Request):
#     body = await request.json()
#     messages = body.get("messages", [])
#     part = messages[0].get("parts")[0]
#     user_message = part.get("text")

#     async def generator():
#         res = await client.chat.completions.create(
#             model="gpt-5.4",
#             messages=[{"role": "user", "content": user_message}],
#             stream=True,
#         )

#         async for chunk in res:
#             if not chunk.choices:
#                 continue

#             if chunk.choices[0].delta.content:
#                 yield chunk.choices[0].delta.content

#     return StreamingResponse(generator(), media_type="text/plain; charset=utf-8")
