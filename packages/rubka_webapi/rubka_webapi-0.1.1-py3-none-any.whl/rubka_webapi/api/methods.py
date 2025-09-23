
from typing import Dict, Any, List, Optional
from rubka_webapi.network.http import HttpClient
from rubka_webapi.types.models import Message, User, Chat, ApiResponse
from rubka_webapi.exceptions import APIError

class APIMethods:
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    async def _send_request(self, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to send requests to the Rubika API."""
        payload = {"method": method, "input": data}
        response = await self.http_client.post("/", payload) # Assuming '/' is the main API endpoint
        api_response = ApiResponse(**response)
        if api_response.status != "OK":
            raise APIError(api_response.message or "Unknown API error", code=api_response.data.get("code"))
        return api_response.data

    async def get_me(self) -> User:
        """Retrieves information about the current authenticated user."""
        data = await self._send_request("getMe", {})
        return User(**data.get("user", {}))

    async def send_text_message(self, chat_id: str, text: str, reply_to_message_id: Optional[str] = None) -> Message:
        """Sends a text message to a specified chat."""
        input_data = {"chat_id": chat_id, "text": text}
        if reply_to_message_id:
            input_data["reply_to_message_id"] = reply_to_message_id
        data = await self._send_request("sendMessage", input_data)
        return Message(**data.get("message", {}))

    async def get_chat_history(self, chat_id: str, limit: int = 20, offset_id: Optional[str] = None) -> List[Message]:
        """Retrieves a list of messages from a chat's history."""
        input_data = {"chat_id": chat_id, "limit": limit}
        if offset_id:
            input_data["offset_id"] = offset_id
        data = await self._send_request("getChatHistory", input_data)
        return [Message(**msg) for msg in data.get("messages", [])]

    async def get_chats(self) -> List[Chat]:
        """Retrieves a list of all chats the user is part of."""
        data = await self._send_request("getChats", {})
        return [Chat(**chat) for chat in data.get("chats", [])]

    # Add more API methods as needed based on Rubika API documentation
    # e.g., edit_message, delete_message, get_chat_info, join_channel, etc.

