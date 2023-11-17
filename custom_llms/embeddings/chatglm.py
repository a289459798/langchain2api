from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from langchain.pydantic_v1 import BaseModel, root_validator
from langchain.schema.embeddings import Embeddings
from langchain.utils import get_from_dict_or_env

logger = logging.getLogger(__name__)


class ChatGLMEmbeddings(BaseModel, Embeddings):
    """`zhipu Embeddings` embedding models."""

    chatglm_api_key: Optional[str] = None
    """Base URL path for API requests, 
    leave blank if not using a proxy or service emulator."""
    chatglm_api_base: Optional[str] = None

    chunk_size: int = 16
    """Chunk size when multiple texts are input"""

    model: str = "text_embedding"
    """Model name
    you could get from https://open.bigmodel.cn/dev/api#text_embedding
    
    """

    client: Any
    """Qianfan client"""

    max_retries: int = 5
    """Max reties times"""

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        values["chatglm_api_key"] = get_from_dict_or_env(
            values, "chatglm_api_key", "CHATGLM_API_KEY"
        )
        values["chatglm_organization"] = get_from_dict_or_env(
            values,
            "chatglm_organization",
            "CHATGLM_ORGANIZATION",
            default="",
        )
        values["chatglm_api_base"] = get_from_dict_or_env(
            values,
            "chatglm_api_base",
            "CHATGLM_API_BASE",
            default="",
        )
        values["chatglm_proxy"] = get_from_dict_or_env(
            values,
            "chatglm_proxy",
            "CHATGLM_PROXY",
            default="",
        )
        try:
            import zhipuai

            zhipuai.api_key = values["chatglm_api_key"]
        except ImportError:
            raise ValueError(
                "Could not import zhipuai python package. "
                "Please install it with `pip install zhipuai`."
            )
        try:
            values["client"] = zhipuai.model_api
        except AttributeError:
            raise ValueError(
                "`zhipuai` has no `model_api` attribute, this is likely "
                "due to an old version of the zhipuai package. Try upgrading it "
                "with `pip install --upgrade zhipuai`."
            )
        return values

    def embed_query(self, text: str) -> List[float]:
        resp = self.embed_documents([text])
        return resp[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds a list of text documents using the AutoVOT algorithm.

        Args:
            texts (List[str]): A list of text documents to embed.

        Returns:
            List[List[float]]: A list of embeddings for each document in the input list.
                            Each embedding is represented as a list of float values.
        """
        lst = []
        
        for chunk in texts:
            params = {"prompt": chunk, "model": self.model}
            resp = self.client.invoke(**params)
            lst.extend([resp["data"]["embedding"]])

        return lst

#     async def aembed_query(self, text: str) -> List[float]:
#         embeddings = await self.aembed_documents([text])
#         return embeddings[0]

#     async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
#         text_in_chunks = [
#             texts[i : i + self.chunk_size]
#             for i in range(0, len(texts), self.chunk_size)
#         ]
#         lst = []
#         for chunk in text_in_chunks:
#             resp = await self.client.ado(texts=chunk)
#             for res in resp["data"]:
#                 lst.extend([res["embedding"]])
#         return lst
