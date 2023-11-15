from uuid import UUID
from langchain.callbacks import AsyncIteratorCallbackHandler, StreamingStdOutCallbackHandler
from typing import Any, Generator
from langchain.schema.messages import BaseMessage

class CustomStreamingIteratorCallbackHandler(StreamingStdOutCallbackHandler):
	tokens = []
	# 记得结束后这里置true
	finish = False

	def on_llm_new_token(self, token: str, **kwargs) -> None:
		self.tokens.append(token)

	def on_llm_end(self, response, **kwargs) -> None:
		self.finish = True

	def on_llm_error(self, error: Exception, **kwargs) -> None:
		self.tokens.append(str(error))

	def generate_tokens(self) -> Generator:
		while not self.finish:  # or self.tokens:
			if self.tokens:
				token = self.tokens.pop(0)
				yield token
			else:
				pass
				# time.sleep(0.02)  # wait for a new token