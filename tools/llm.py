from langchain.chat_models import ChatOpenAI, ChatHunyuan
from tools.error import Abort
from langchain.callbacks.base import BaseCallbackHandler
from custom_llms.chat_models import ChatChatGLM
import os
from langchain.embeddings import OpenAIEmbeddings
from custom_llms.embeddings import ChatGLMEmbeddings

def GetLLM(model: str, callback: BaseCallbackHandler = None):
	if model == 'openai':
		os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
		os.environ["OPENAI_API_BASE"] = os.getenv('OPENAI_API_BASE')
		return ChatOpenAI(temperature=0.9, model_name='gpt-3.5-turbo', streaming=True, callbacks=[callback], verbose=True)
	elif model == 'hunyuan':
		return ChatHunyuan(
			hunyuan_app_id=os.getenv('HUNYUAN_APP_ID'),
    			hunyuan_secret_id=os.getenv('HUNYUAN_SECRET_ID'),
   			hunyuan_secret_key=os.getenv('HUNYUAN_SECRET_KEY'),
    			streaming=True,
			verbose=True,
			callbacks=[callback]
		)
	elif model == 'chatglm':
		return ChatChatGLM(
			chatglm_api_key=os.getenv('CHATGLM_API_KEY'),
			chatglm_api_base=os.getenv('CHATGLM_API_BASE'),
    			streaming=True,
			verbose=True,
			callbacks=[callback]
		)
	else:
		Abort(500, '模型不支持')

def GetEmbeddings(model: str):
	if model == 'openai':
		return OpenAIEmbeddings()
	elif model == 'chatglm':
		return ChatGLMEmbeddings(
			chatglm_api_key=os.getenv('CHATGLM_API_KEY'),
			chatglm_api_base=os.getenv('CHATGLM_API_BASE')
		)
	else:
		return OpenAIEmbeddings()