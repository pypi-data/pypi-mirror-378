from typing import Any, Callable, Dict, Optional, Union
import socketio
import threading
import asyncio
from .exceptions import ConnectionError, AuthenticationError

_DEFAULT_PATH = "/socket.io"

class WSBase:
    def __init__(self, url: str, api_token: Optional[str], auto_reconnect: bool):
        self.url = url.rstrip("/")
        self.api_token = api_token
        self.auto_reconnect = auto_reconnect

class SyncWS(WSBase):
    def __init__(self, url: str, api_token: Optional[str], auto_reconnect: bool = True):
        super().__init__(url, api_token, auto_reconnect)
        self._sio = socketio.Client(reconnection=auto_reconnect)
        self._event_handlers: Dict[str, Callable[..., None]] = {}
        self._connected = threading.Event()

        @self._sio.event
        def connect():
            self._connected.set()

        @self._sio.event
        def disconnect():
            self._connected.clear()

        @self._sio.on("*")
        def catch_all(event, data=None):
            handler = self._event_handlers.get(event)
            if handler:
                try:
                    if data is None:
                        handler()
                    else:
                        handler(data)
                except Exception:
                    pass

    def connect(self):
        headers = {}
        if self.api_token:
            headers["apitoken"] = self.api_token
        try:
            self._sio.connect(self.url, headers=headers)
        except socketio.exceptions.ConnectionError as e:
            if "401" in str(e):
                raise AuthenticationError("Unauthorized: invalid or missing API token")
            raise ConnectionError(str(e))
        self._connected.wait(5)

    def disconnect(self):
        try:
            self._sio.disconnect()
        except Exception:
            pass

    def emit(self, event: str, data: Optional[Dict[str, Any]] = None, callback: Optional[Callable] = None):
        self._sio.emit(event, data or {}, callback=callback)

    def on(self, event: str, handler: Callable[..., None]):
        self._event_handlers[event] = handler

    def off(self, event: str):
        self._event_handlers.pop(event, None)


class AsyncWS(WSBase):
    def __init__(self, url: str, api_token: Optional[str], auto_reconnect: bool = True):
        super().__init__(url, api_token, auto_reconnect)
        self._sio = socketio.AsyncClient(reconnection=auto_reconnect)
        self._event_handlers: Dict[str, Callable[..., Any]] = {}
        self._connected = asyncio.Event()

        @self._sio.event
        async def connect():
            self._connected.set()

        @self._sio.event
        async def disconnect():
            self._connected.clear()

    async def connect(self):
        headers = {}
        if self.api_token:
            headers["apitoken"] = self.api_token
        try:
            await self._sio.connect(self.url, headers=headers)
        except socketio.exceptions.ConnectionError as e:
            if "401" in str(e):
                raise AuthenticationError("Unauthorized: invalid or missing API token")
            raise ConnectionError(str(e))
        try:
            await asyncio.wait_for(self._connected.wait(), timeout=5)
        except asyncio.TimeoutError:
            pass

    async def disconnect(self):
        try:
            await self._sio.disconnect()
        except Exception:
            pass

    async def emit(self, event: str, data: Optional[Dict[str, Any]] = None, callback: Optional[Callable] = None):
        await self._sio.emit(event, data or {}, callback=callback)

    def on(self, event: str, handler: Callable[..., Any]):
        self._sio.on(event)(handler)

    def off(self, event: str):
        self._sio.handlers.get("/", {}).pop(event, None)
