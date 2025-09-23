
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List

from rubka_webapi.network.http import HttpClient
from rubka_webapi.network.websocket import WebSocketClient
from rubka_webapi.client.session import SessionManager
from rubka_webapi.api.methods import APIMethods
from rubka_webapi.types.models import AuthData, Message, User, Chat
from rubka_webapi.exceptions import AuthError, NetworkError, RubkaWebAPIException, InvalidSessionError

class Client:
    def __init__(
        self,
        session_name: Optional[str] = None,
        auth_data: Optional[AuthData] = None,
        base_url: str = "https://messengerg2c4.iranlms.ir", # Example Rubika API base URL
        websocket_uri: str = "wss://messengerg2c4.iranlms.ir/ws", # Example Rubika WebSocket URI
        timeout: int = 30,
        session_dir: str = ".rubi_sessions",
    ):
        self.session_name = session_name
        self._auth_data = auth_data
        self.base_url = base_url
        self.websocket_uri = websocket_uri
        self.timeout = timeout
        self.session_manager = SessionManager(session_name or "default", Path(session_dir))

        self.http_client = HttpClient(base_url=self.base_url, timeout=self.timeout)
        self.api = APIMethods(self.http_client) # Integrate API methods
        self.websocket_client: Optional[WebSocketClient] = None

        self._message_handlers: List[Callable[[Message], Any]] = []
        self._event_handlers: Dict[str, List[Callable[[Dict[str, Any]], Any]]] = {}

    async def _on_websocket_message(self, data: Dict[str, Any]):
        # Process incoming WebSocket messages and dispatch to handlers
        print(f"Received WebSocket message: {data}") # For debugging
        # Example: if data is a new message, parse it and call message handlers
        if data.get("type") == "message" and data.get("object_type") == "Message":
            try:
                message = Message(**data.get("payload", {}))
                for handler in self._message_handlers:
                    await handler(message)
            except Exception as e:
                print(f"Error processing message: {e}")
        
        event_type = data.get("event_type") # Assuming a generic event_type field
        if event_type and event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                await handler(data)

    async def _on_websocket_error(self, error: Exception):
        print(f"WebSocket error: {error}")
        # Implement reconnection logic or error notification

    async def _on_websocket_close(self):
        print("WebSocket closed.")
        # Implement reconnection logic

    async def start(self):
        if self._auth_data is None and self.session_name:
            try:
                self._auth_data = self.session_manager.load_session()
            except InvalidSessionError:
                raise AuthError("No valid session found. Please provide auth_data or log in.")
        
        if not self._auth_data:
            raise AuthError("Authentication data is required to start the client.")

        # Initialize WebSocket client after authentication data is available
        self.websocket_client = WebSocketClient(
            uri=self.websocket_uri,
            on_message=self._on_websocket_message,
            on_error=self._on_websocket_error,
            on_close=self._on_websocket_close,
        )
        await self.websocket_client.connect()
        print("Client started. Listening for events...")

        # Keep the client running
        while True:
            await asyncio.sleep(1) # Keep the event loop alive

    async def stop(self):
        if self.websocket_client:
            await self.websocket_client.disconnect()
        await self.http_client.close()
        print("Client stopped.")

    def on_message(self, handler: Callable[[Message], Any]):
        self._message_handlers.append(handler)
        return handler

    def on_event(self, event_type: str):
        def decorator(handler: Callable[[Dict[str, Any]], Any]):
            if event_type not in self._event_handlers:
                self._event_handlers[event_type] = []
            self._event_handlers[event_type].append(handler)
            return handler
        return decorator

    async def login(self, auth_key: str, private_key: str):
        # This is a simplified login. Real Rubika login might involve more steps.
        auth_data = AuthData(auth_key=auth_key, private_key=private_key)
        self.session_manager.save_session(auth_data)
        self._auth_data = auth_data
        print("Login successful and session saved.")

    async def run(self):
        try:
            await self.start()
        except KeyboardInterrupt:
            print("Client interrupted by user.")
        except Exception as e:
            print(f"Client encountered an error: {e}")
        finally:
            await self.stop()



