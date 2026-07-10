import asyncio
from typing import List, Dict, Any
from google import genai
from google.genai import types

class LLMService:
    def __init__(self, api_key: str, model_name: str = "gemini-3.1-flash-lite"):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        
    async def _generate(self, system_instruction: str, user_content: str, history: List[Dict[str, str]] = None) -> str:
        def _call_api():
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0,
            )
            
            contents = []
            if history:
                for msg in history:
                    role = "user" if msg.get("role") == "user" else "model"
                    contents.append(
                        types.Content(role=role, parts=[types.Part.from_text(text=msg.get("content", ""))])
                    )
            
            contents.append(
                types.Content(role="user", parts=[types.Part.from_text(text=user_content)])
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            return response.text
            
        return await asyncio.to_thread(_call_api)

    async def generate_answer(self, query: str, chunks: List[Dict[str, Any]], history: List[Dict[str, str]] = None) -> str:
        if not chunks:
            return "I cannot find any relevant documents to answer your question."
            
        context_texts = []
        for i, chunk in enumerate(chunks):
            payload = chunk.get("payload", {})
            text = payload.get("text", "")
            doc_name = payload.get("document_name", "Unknown Document")
            context_texts.append(f"--- Source [{i+1}]: {doc_name} ---\n{text}")
            
        joined_context = "\n\n".join(context_texts)
        
        system_instruction = (
            "You are a helpful and precise Q&A assistant.\n"
            "You must answer the user's question based ONLY on the provided context below.\n"
            "If the answer cannot be found in the context, clearly state \"I cannot find the answer to this question in the provided documents.\" Do not invent or hallucinate information.\n"
            "When providing information from the context, please cite the Source number(s) (e.g., [1], [2])."
        )
        
        user_content = f"CONTEXT:\n{joined_context}\n\nUSER QUESTION:\n{query}"
        
        try:
            return await self._generate(system_instruction, user_content, history)
        except Exception as e:
            print(f"Error calling Gemini LLM: {e}")
            return "An error occurred while generating the answer."

    async def rewrite_question(self, current_question: str, history: List[Dict[str, str]]) -> str:
        if not history:
            return current_question
            
        system_instruction = (
            "You are a query rewriting assistant. Your job is to rewrite the user's latest query into a clear, self-contained search query.\n\n"
            "RULES:\n"
            "1. Resolve any pronouns or references (e.g., \"it\", \"there\", \"that shop\", \"แล้ว...\", \"มั้ย\") using the conversation history.\n"
            "2. Keep the rewritten query concise and specific.\n"
            "3. If the query is already clear and self-contained with no references to prior context, return it exactly as-is.\n"
            "4. Preserve the original language (Thai or English) of the query.\n"
            "5. Output ONLY the rewritten query text. No explanations, no quotes, no prefixes."
        )
        
        try:
            response_text = await self._generate(system_instruction, current_question, history)
            rewritten = response_text.strip().strip('"').strip("'")
            return rewritten if rewritten else current_question
        except Exception as e:
            print(f"Error rewriting question: {e}")
            return current_question

