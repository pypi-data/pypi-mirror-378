
import httpx
from typing import Dict, Any, Optional
from ..exceptions import NetworkError, APIError, RubkaWebAPIException

class HttpClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=timeout)

    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = await self.client.post(endpoint, json=data)
            response.raise_for_status()  # Raise an exception for 4xx/5xx responses
            return response.json()
        except httpx.RequestError as exc:
            raise NetworkError(f"An error occurred while requesting {exc.request.url!r}: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code >= 400 and exc.response.status_code < 500:
                # Client error, potentially an API error
                try:
                    error_data = exc.response.json()
                    message = error_data.get("message", "Unknown API error")
                    code = error_data.get("code", exc.response.status_code)
                    raise APIError(message, code) from exc
                except ValueError:
                    raise APIError(f"API error: {exc.response.text}", exc.response.status_code) from exc
            else:
                # Server error or other HTTP error
                raise NetworkError(f"HTTP error {exc.response.status_code} for {exc.request.url!r}: {exc.response.text}") from exc
        except Exception as exc:
            raise RubkaWebAPIException(f"An unexpected error occurred: {exc}") from exc

    async def close(self):
        await self.client.close()

