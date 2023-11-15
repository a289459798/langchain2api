from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, BaseMessage
from langchain.callbacks import AsyncIteratorCallbackHandler, StreamingStdOutCallbackHandler
from starlette.responses import StreamingResponse
import asyncio
from langchain.memory import ConversationBufferMemory
from tools.error import Abort
from langchain.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
import shutil
from langchain.chains import ConversationalRetrievalChain
from handlers.custom_streaming_iter import CustomStreamingIteratorCallbackHandler
import threading

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


@router.post('/doc')
async def doc(file: UploadFile = File(), prompt: str = Form()):
	with open(file.filename, 'wb') as buffer:
		shutil.copyfileobj(file.file, buffer)
	if file.content_type == 'text/plain':
		loader = TextLoader(file.filename, encoding='utf8')
	elif file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
		return
	else:
		Abort(400, '文件类型不支持')

	callback = CustomStreamingIteratorCallbackHandler()
	llm = ChatOpenAI(temperature=0.9, model_name='gpt-3.5-turbo', streaming=True, callbacks=[callback])
	index = VectorstoreIndexCreator().from_loaders([loader])
	retriever = index.vectorstore.as_retriever()
	qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever)

	thread = threading.Thread(target=f, args=(qa, {'question': prompt, 'chat_history': []}))
	thread.start()

	resp = StreamingResponse(callback.generate_tokens(), media_type='text/event-stream')
	# print(resp.body)
	return resp

async def generate_stream_response(_callback: AsyncIteratorCallbackHandler, llm: ChatOpenAI, messages: list[BaseMessage]):
    """流式响应"""
    
    task = asyncio.create_task(llm.apredict_messages(messages))
    message = ''
    async for token in _callback.aiter():
        message += token
        yield token
    memory.chat_memory.add_ai_message(message)
    await task

def f(qa, data):
	qa.run(data)