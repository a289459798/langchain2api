from fastapi import APIRouter
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, BaseMessage
from langchain.callbacks import AsyncIteratorCallbackHandler
from starlette.responses import StreamingResponse
import asyncio

router = APIRouter(
	prefix='/chat',
	tags=['chat']
)

class Chat(BaseModel):
	chatId: str = None
	prompt: str


@router.post('')
async def chat(chat: Chat):
	callback = AsyncIteratorCallbackHandler()
	llm = ChatOpenAI(temperature=0.9, model_name='gpt-3.5-turbo', streaming=True, callbacks=[callback])
	messages = [HumanMessage(content=chat.prompt)]
	return StreamingResponse(generate_stream_response(callback, llm, messages), media_type='text/event-stream')


async def generate_stream_response(_callback, llm: ChatOpenAI, messages: list[BaseMessage]):
    """流式响应"""
    task = asyncio.create_task(llm.apredict_messages(messages))
    async for token in _callback.aiter():
        yield token

    await task