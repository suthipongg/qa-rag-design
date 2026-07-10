import asyncio
from abc import ABC, abstractmethod
from typing import Any
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
    async def embed_documents(self, texts: list[str]) -> list[dict[str, Any]]:
        """Generate dense and sparse embeddings for a list of documents."""
        pass

    @abstractmethod
    async def embed_query(self, text: str) -> dict[str, Any]:
        """Generate dense and sparse embedding for a single query."""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Return the dimension of the dense embedding vectors."""
        pass


class BGEM3EmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name:str="BAAI/bge-m3"):
        self.model = None
        self.model_name = model_name

    async def embed_documents(self, texts: list[str]) -> list[dict[str, Any]]:
        self.model = get_bge_model(self.model_name)
        if not texts:
            return []
        
        def _encode():
            output = self.model.encode(
                texts, 
                return_dense=True, 
                return_sparse=True, 
                return_colbert_vecs=False
            )
            dense_vecs = output['dense_vecs']
            lexical_weights = output.get('lexical_weights', [])
            
            results = []
            for i, dense in enumerate(dense_vecs):
                dense_list = dense.tolist() if isinstance(dense, np.ndarray) else list(map(float, dense))
                sparse = None
                
                if lexical_weights and i < len(lexical_weights):
                    lex = lexical_weights[i]
                    indices = []
                    values = []
                    for k, v in lex.items():
                        indices.append(int(k))
                        values.append(float(v))
                    if indices:
                        sparse = {"indices": indices, "values": values}
                        
                results.append({"dense": dense_list, "sparse": sparse})
            return results

        return await asyncio.to_thread(_encode)

    async def embed_query(self, text: str) -> dict[str, Any]:
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

    async def embed_documents(self, texts: list[str]) -> list[dict[str, Any]]:
        if not texts:
            return []
        
        from google.genai import types
        contents = [types.Content(parts=[types.Part.from_text(text=txt)]) for txt in texts]
        
        def _embed():
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=contents,
            )
            return [{"dense": embedding.values, "sparse": None} for embedding in response.embeddings]
        return await asyncio.to_thread(_embed)

    async def embed_query(self, text: str) -> dict[str, Any]:
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
