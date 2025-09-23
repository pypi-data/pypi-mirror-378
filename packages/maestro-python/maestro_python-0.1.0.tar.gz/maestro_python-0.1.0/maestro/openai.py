import os 
import httpx 
from typing import Any, Dict, List, Optional
import inspect 
import time

BASE_URL = os.getenv("MAESTRO_API_URL", "http://localhost:8000/v1")

class ChatCompletions:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def create(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        caller = inspect.stack()[1]
        start = time.perf_counter()
        payload = {"model": model, "messages": messages, "llm_addr": f"{caller.filename}/{caller.function}:{caller.lineno}", "start": start, **kwargs}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        with httpx.Client() as client:
            resp = client.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            result = resp.json() 
            return result

class Chat:
    def __init__(self, api_key: str):
        self.completions = ChatCompletions(api_key)


class Responses:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def create(self, model: str, **kwargs) -> Dict[str, Any]:
        caller = inspect.stack()[1]
        start = time.perf_counter()
        payload = {"model": model, "llm_addr": f"{caller.filename}/{caller.function}:{caller.lineno}", "start": start, **kwargs}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        with httpx.Client() as client:
            resp = client.post(f"{BASE_URL}/responses", json=payload, headers=headers)
            resp.raise_for_status()
            result = resp.json()
            return result 

class OpenAI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass api_key parameter.")

        self.chat = Chat(self.api_key)
        self.responses = Responses(self.api_key)

