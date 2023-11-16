from langchain.chat_models import ChatOpenAI, ChatHunyuan
from tools.error import Abort
from langchain.callbacks.base import BaseCallbackHandler

def GetLLM(model: str, callback: BaseCallbackHandler = None):
	if model == 'openai':
		return ChatOpenAI(temperature=0.9, model_name='gpt-3.5-turbo', streaming=True, callbacks=[callback], verbose=True)
	elif model == 'huanyuan':
		return ChatHunyuan(
			hunyuan_app_id="YOUR_APP_ID",
    			hunyuan_secret_id="YOUR_SECRET_ID",
   			hunyuan_secret_key="YOUR_SECRET_KEY",
    			streaming=True,
		)
	elif model == 'chatgml':
		return
	else:
		Abort(500, '模型不支持')