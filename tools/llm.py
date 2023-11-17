from langchain.chat_models import ChatOpenAI, ChatHunyuan
from tools.error import Abort
from langchain.callbacks.base import BaseCallbackHandler
import os

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
	elif model == 'chatgml':
		return
	else:
		Abort(500, '模型不支持')