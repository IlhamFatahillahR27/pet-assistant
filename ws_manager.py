import json
import asyncio
from typing import List, Dict, Any, Callable
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._loop: asyncio.AbstractEventLoop = None

    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
            print("[WebSocket] Event loop otomatis tersimpan.")
        self.active_connections.append(websocket)
        print(f"[WebSocket] Client terhubung. Total client: {len(self.active_connections)}")


    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[WebSocket] Client terputus. Sisa client: {len(self.active_connections)}")

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
        except Exception as e:
            print(f"[WebSocket Error] Gagal mengirim pesan personal: {e}")

    async def broadcast(self, event_type: str, data: Any):
        """Broadcast pesan terstruktur ke seluruh WebSocket client terhubung (async)."""
        payload = {
            "event": event_type,
            "data": data
        }
        message_str = json.dumps(payload, ensure_ascii=False)
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                print(f"[WebSocket Broadcast Error] {e}")
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

    def broadcast_threadsafe(self, event_type: str, data: Any):
        """
        Thread-safe broadcast dari background thread (seperti STT, TTS, Wake Word)
        ke event loop FastAPI WebSocket.
        """
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self.broadcast(event_type, data), self._loop)
        else:
            print(f"[WebSocket Warning] Event loop belum aktif. Broadcast '{event_type}' diabaikan.")

# Singleton instance
ws_manager = ConnectionManager()
