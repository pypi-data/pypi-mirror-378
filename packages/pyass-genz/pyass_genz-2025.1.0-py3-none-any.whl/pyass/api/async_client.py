# pyass🍑/src/pyass/api/async_client.py

import asyncio
import aiohttp
from typing import List, Optional, Dict, Any
from urllib.parse import urlencode

class PyAssAsyncClient:
    """
    Async HTTP client for pyass🍑 API.
    Use this to talk to a local or remote pyass API server.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        """Make HTTP request"""
        url = f"{self.base_url}{path}"
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status >= 400:
                    text = await response.text()
                    raise Exception(f"API Error {response.status}: {text}")
                return await response.json()
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return await self._request("GET", "/health")

    async def define(self, term: str) -> Dict[str, Any]:
        """Get slang definition"""
        return await self._request("GET", f"/define/{term}")

    async def random_slang(
        self,
        count: int = 1,
        persona: Optional[str] = None,
        region: Optional[str] = None,
        platform: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get random slang"""
        params: Dict[str, Any] = {"count": count}
        if persona:
            params["persona"] = persona
        if region:
            params["region"] = region
        if platform:
            params["platform"] = platform

        return await self._request("GET", f"/random?{urlencode(params)}")

    async def translate(
        self,
        text: str,
        tone: str = "casual",
        intensity: float = 0.7,
        persona: Optional[str] = None
    ) -> Dict[str, Any]:
        """Translate text to slang"""
        payload = {
            "text": text,
            "tone": tone,
            "intensity": intensity
        }
        if persona:
            payload["persona"] = persona

        return await self._request("POST", "/translate", json=payload)

    async def search(
        self,
        query: str,
        fuzzy: bool = False,
        threshold: float = 0.6,
        region: Optional[str] = None,
        platform: Optional[str] = None,
        min_popularity: int = 0,
        max_popularity: int = 100
    ) -> List[Dict[str, Any]]:
        """Search slang"""
        params: Dict[str, Any] = {
            "query": query,
            "fuzzy": str(fuzzy).lower(),
            "threshold": threshold,
            "min_popularity": min_popularity,
            "max_popularity": max_popularity
        }
        if region:
            params["region"] = region
        if platform:
            params["platform"] = platform

        return await self._request("GET", f"/search?{urlencode(params)}")

    async def by_persona(self, persona: str, count: int = 5) -> List[Dict[str, Any]]:
        """Get slang by persona"""
        return await self._request("GET", f"/mood/{persona}?count={count}")

    async def trending(
        self,
        region: Optional[str] = None,
        platform: Optional[str] = None,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """Get trending slang"""
        params: Dict[str, Any] = {"count": count}
        if region:
            params["region"] = region
        if platform:
            params["platform"] = platform

        return await self._request("GET", f"/trending?{urlencode(params)}")

    async def stats(self) -> Dict[str, Any]:
        """Get API stats"""
        return await self._request("GET", "/stats")

    # Quiz methods (simplified)
    async def start_quiz(self, num_questions: int = 5, adaptive: bool = True) -> List[Dict[str, Any]]:
        """Start quiz"""
        payload = {"num_questions": num_questions, "adaptive": adaptive}
        return await self._request("POST", "/quiz/start", json=payload)

    async def submit_quiz_answer(self, session_id: str, question_id: int, answer_index: int) -> Dict[str, Any]:
        """Submit quiz answer"""
        payload = {"question_id": question_id, "answer_index": answer_index}
        return await self._request("POST", f"/quiz/submit?session_id={session_id}", json=payload)

# Convenience async context manager
async def get_client(base_url: str = "http://localhost:8000") -> PyAssAsyncClient:
    """Get async client (use in async with)"""
    client = PyAssAsyncClient(base_url)
    await client.__aenter__()
    return client

# Example usage function
async def example_usage():
    """Example of how to use the async client"""
    async with PyAssAsyncClient("http://localhost:8000") as client:
        # Health check
        health = await client.health_check()
        print(f"Health: {health}")

        # Define term
        try:
            rizz = await client.define("rizz")
            print(f"Rizz: {rizz['definition']}")
        except Exception as e:
            print(f"Error: {e}")

        # Translate
        translated = await client.translate("I am very tired", tone="dramatic", intensity=0.9)
        print(f"Translated: {translated['translated']}")

        # Random slang
        randoms = await client.random_slang(count=3, persona="sigma")
        for slang in randoms:
            print(f"🍑 {slang['term']}: {slang['definition']}")

        # Search
        results = await client.search("gyatt", fuzzy=True, threshold=0.4)
        print(f"Found {len(results)} results")

if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
