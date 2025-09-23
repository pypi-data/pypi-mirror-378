
import websockets
import asyncio
import json
from typing import Callable, Dict, Any, Optional
from ..exceptions import NetworkError, PyrubiException

class WebSocketClient:
    def __init__(self, uri: str, on_message: Callable[[Dict[str, Any]], Any], on_error: Callable[[Exception], Any], on_close: Callable[[], Any]):
        self.uri = uri
        self.on_message = on_message
        self.on_error = on_error
        self.on_close = on_close
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._run_task: Optional[asyncio.Task] = None

    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.uri)
            self._run_task = asyncio.create_task(self._run())
        except websockets.exceptions.WebSocketException as exc:
            await self.on_error(NetworkError(f"WebSocket connection failed: {exc}") from exc)
        except Exception as exc:
            await self.on_error(PyrubiException(f"An unexpected error occurred during WebSocket connection: {exc}") from exc)

    async def _run(self):
        try:
            while True:
                message = await self.websocket.recv()
                if isinstance(message, str):
                    data = json.loads(message)
                    await self.on_message(data)
        except websockets.exceptions.ConnectionClosedOK:
            pass  # Connection closed normally
        except websockets.exceptions.WebSocketException as exc:
            await self.on_error(NetworkError(f"WebSocket error: {exc}") from exc)
        except json.JSONDecodeError as exc:
            await self.on_error(PyrubiException(f"Failed to decode WebSocket message: {exc}") from exc)
        except Exception as exc:
            await self.on_error(PyrubiException(f"An unexpected error occurred in WebSocket loop: {exc}") from exc)
        finally:
            await self.on_close()

    async def send(self, data: Dict[str, Any]):
        if self.websocket and self.websocket.open:
            try:
                await self.websocket.send(json.dumps(data))
            except websockets.exceptions.WebSocketException as exc:
                await self.on_error(NetworkError(f"Failed to send WebSocket message: {exc}") from exc)
        else:
            raise NetworkError("WebSocket is not connected.")

    async def disconnect(self):
        if self.websocket and self.websocket.open:
            await self.websocket.close()
        if self._run_task:
            self._run_task.cancel()
            try:
                await self._run_task
            except asyncio.CancelledError:
                pass
        

