from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, BaseMessage, AIMessage
from langchain.callbacks import AsyncIteratorCallbackHandler
from starlette.responses import StreamingResponse
import asyncio
from langchain.memory import ConversationBufferMemory
from tools.error import Abort
from langchain.document_loaders import TextLoader, UnstructuredWordDocumentLoader, UnstructuredExcelLoader
from langchain.indexes import VectorstoreIndexCreator
import shutil
from langchain.chains import ConversationalRetrievalChain
from handlers.custom_streaming_iter import CustomStreamingIteratorCallbackHandler
import threading
from tools.llm import GetLLM, GetEmbeddings

router = APIRouter(
	prefix='/chat',
	tags=['chat']
)

memory = ConversationBufferMemory()

class Chat(BaseModel):
	chatId: str = None
	prompt: str
	model: str = 'openai'


@router.post('')
async def chat(chat: Chat):
	callback = AsyncIteratorCallbackHandler()
	llm = GetLLM(chat.model, callback)
	memory.chat_memory.add_user_message(chat.prompt)
	resp = StreamingResponse(generate_stream_response(callback, llm, memory.chat_memory.messages), media_type='text/event-stream')
	return resp


@router.post('/doc')
async def doc(file: UploadFile = File(), prompt: str = Form(), model: str = Form()):
	print(file.content_type)
	filepath = 'tmp/' + file.filename
	with open(filepath, 'wb') as buffer:
		shutil.copyfileobj(file.file, buffer)
	if file.content_type == 'text/plain':
		loader = TextLoader(filepath, encoding='utf8')
	elif file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or file.content_type == 'application/msword':
		loader = UnstructuredWordDocumentLoader(filepath)
	elif file.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
		loader = UnstructuredExcelLoader(filepath)
	else:
		Abort(400, '文件类型不支持')

	callback = CustomStreamingIteratorCallbackHandler()
	llm = GetLLM(model, callback)
	index = VectorstoreIndexCreator(embedding=GetEmbeddings(model)).from_loaders([loader])
	retriever = index.vectorstore.as_retriever()
	qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever)

	def cb():
		qa({'question': prompt, 'chat_history': []})
	thread = threading.Thread(target=cb)
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