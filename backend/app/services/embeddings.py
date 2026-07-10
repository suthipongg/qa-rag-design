import asyncio
from abc import ABC, abstractmethod
from typing import List
import numpy as np

_bge_model = None

def get_bge_model(model_name:str):
    global _bge_model
    if _bge_model is None:
        from FlagEmbedding import BGEM3FlagModel
        print(f"Loading local BGE-M3 model ({model_name})...")
        try:
            import torch
            use_fp16 = torch.cuda.is_available()
        except ImportError:
            use_fp16 = False
            
        _bge_model = BGEM3FlagModel(model_name, use_fp16=use_fp16)
        print("BGE-M3 model loaded successfully.")
    return _bge_model


class BaseEmbeddingProvider(ABC):
    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate dense embeddings for a list of documents."""
        pass

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """Generate dense embedding for a single query."""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Return the dimension of the embedding vectors."""
        pass


class BGEM3EmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name:str="BAAI/bge-m3"):
        self.model = None
        self.model_name = model_name

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        self.model = get_bge_model(self.model_name)
        if not texts:
            return []
        
        def _encode():
            output = self.model.encode(
                texts, 
                return_dense=True, 
                return_sparse=False, 
                return_colbert_vecs=False
            )
            dense_vecs = output['dense_vecs']
            if isinstance(dense_vecs, np.ndarray):
                return dense_vecs.tolist()
            return [list(map(float, vec)) for vec in dense_vecs]

        return await asyncio.to_thread(_encode)

    async def embed_query(self, text: str) -> List[float]:
        embeddings = await self.embed_documents([text])
        return embeddings[0]

    def get_dimension(self) -> int:
        return 1024


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name:str="text-embedding-004", api_key:str=""):
        from google import genai
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment settings.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        
        def _embed():
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=texts,
            )
            return [embedding.values for embedding in response.embeddings]
        return await asyncio.to_thread(_embed)

    async def embed_query(self, text: str) -> List[float]:
        embeddings = await self.embed_documents([text])
        return embeddings[0]

    def get_dimension(self) -> int:
        return 3072


_provider_instance = None

def get_embedding_provider(provider:str, model_name:str, api_key:str="") -> BaseEmbeddingProvider:
    global _provider_instance
    if _provider_instance is None:
        provider_type = provider.lower()
        
        if provider_type == "bge-m3":
            try:
                _provider_instance = BGEM3EmbeddingProvider(model_name=model_name)
            except Exception as e:
                print(f"⚠️ Failed to load local BGE-M3 provider: {e}")
                print("Falling back to Gemini Embedding Provider...")
                _provider_instance = GeminiEmbeddingProvider(model_name=model_name, api_key=api_key)
        elif provider_type == "gemini":
            _provider_instance = GeminiEmbeddingProvider(model_name=model_name, api_key=api_key)
        else:
            raise ValueError(f"Unknown embedding provider: {provider_type}")
            
    return _provider_instance
