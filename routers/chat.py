from fastapi import APIRouter
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, BaseMessage
from langchain.callbacks import AsyncIteratorCallbackHandler
from starlette.responses import StreamingResponse
import asyncio
from langchain.memory import ConversationBufferMemory

router = APIRouter(
	prefix='/chat',
	tags=['chat']
)

memory = ConversationBufferMemory()

class Chat(BaseModel):
	chatId: str = None
	prompt: str


@router.post('')
async def chat(chat: Chat):
	callback = AsyncIteratorCallbackHandler()
	llm = ChatOpenAI(temperature=0.9, model_name='gpt-3.5-turbo', streaming=True, callbacks=[callback], verbose=True)
	memory.chat_memory.add_user_message(chat.prompt)
	resp = StreamingResponse(generate_stream_response(callback, llm, memory.chat_memory.messages), media_type='text/event-stream')
	return resp

async def generate_stream_response(_callback, llm: ChatOpenAI, messages: list[BaseMessage]):
    """流式响应"""
    
    task = asyncio.create_task(llm.apredict_messages(messages))
    message = ''
    async for token in _callback.aiter():
        message += token
        yield token
    memory.chat_memory.add_ai_message(message)
    await task