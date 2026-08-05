import asyncio
import threading
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from settings_manager import settings_manager
from ws_manager import ws_manager
import gemini_brain
import stt
import tts
import wake_word_listener

app = FastAPI(
    title="Pet Assistant Backend API",
    description="FastAPI & WebSocket Server untuk Pet Assistant",
    version="2.0.0"
)

# CORS middleware agar frontend (Tauri/React) bisa terhubung tanpa kendala CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_running_loop()
    ws_manager.set_event_loop(loop)
    print("[SERVER] Pet Assistant FastAPI Server berhasil dijalankan.")
    
    # Auto-start Wake Word Listener jika diaktifkan di settings.json
    settings = settings_manager.get_settings().get("wake_word", {})
    if settings.get("enabled", False):
        try:
            wake_word_listener.start_global_wake_word_listener()
        except Exception as e:
            print(f"[Startup Warning] Gagal memulai Wake Word listener: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    wake_word_listener.stop_global_wake_word_listener()
    print("[SERVER] Server dihentikan.")


# Pydantic Schemas
class ChatRequest(BaseModel):
    prompt: str

class SpeakRequest(BaseModel):
    text: str
    rate: Optional[int] = None
    volume: Optional[float] = None
    language: Optional[str] = None

class SettingsUpdateRequest(BaseModel):
    ai_model: Optional[str] = None
    language: Optional[str] = None
    tts: Optional[Dict[str, Any]] = None
    wake_word: Optional[Dict[str, Any]] = None

# REST Endpoints

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "service": "Pet Assistant Backend",
        "version": "2.0.0"
    }

@app.get("/api/settings", tags=["Settings"])
def get_settings():
    return settings_manager.get_settings()

@app.put("/api/settings", tags=["Settings"])
async def update_settings(payload: SettingsUpdateRequest):
    update_data = {k: v for k, v in payload.dict().items() if v is not None}
    updated = settings_manager.update_settings(update_data)
    
    # Broadcast perubahan settings ke seluruh WebSocket client
    await ws_manager.broadcast("settings_updated", updated)
    return {"status": "success", "settings": updated}

@app.post("/api/chat", tags=["AI Chat"])
async def chat_with_gemini(req: ChatRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt tidak boleh kosong")
    
    response_text = gemini_brain.send_prompt_request(req.prompt)
    return {
        "prompt": req.prompt,
        "response": response_text
    }

@app.post("/api/stt/listen", tags=["Audio & Speech"])
def trigger_stt(background_tasks: BackgroundTasks):
    """Pemicu proses listening STT di background thread."""
    def run_stt():
        stt.process_voice_command()

    background_tasks.add_task(run_stt)
    return {"status": "listening_triggered", "message": "Proses STT dimulai"}

@app.post("/api/tts/speak", tags=["Audio & Speech"])
def trigger_tts(req: SpeakRequest):
    """Pemicu pembacaan teks suara (TTS)."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Teks tidak boleh kosong")
    
    tts.text_to_speech(
        text=req.text,
        rate=req.rate,
        volume=req.volume,
        language=req.language
    )
    return {"status": "speaking_triggered", "text": req.text}

@app.get("/api/tts/voices", tags=["Audio & Speech"])
def list_voices():
    """Mendapatkan daftar suara yang tersedia di sistem."""
    return {"voices": tts.get_available_voices()}

@app.post("/api/wakeword/start", tags=["Wake Word"])
def start_wakeword():
    listener = wake_word_listener.start_global_wake_word_listener()
    settings_manager.update_settings({"wake_word": {"enabled": True}})
    return {"status": "started", "target_models": listener.target_models}

@app.post("/api/wakeword/stop", tags=["Wake Word"])
def stop_wakeword():
    wake_word_listener.stop_global_wake_word_listener()
    settings_manager.update_settings({"wake_word": {"enabled": False}})
    return {"status": "stopped"}

# WebSocket Endpoint

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    # Kirim status koneksi & settings saat ini ke client baru
    await ws_manager.send_personal_message(
        {
            "event": "connected",
            "data": {
                "message": "Terhubung ke Pet Assistant WebSocket Server",
                "settings": settings_manager.get_settings()
            }
        },
        websocket
    )
    
    try:
        while True:
            data_str = await websocket.receive_text()
            try:
                import json
                payload = json.loads(data_str)
                action = payload.get("action")
                
                if action == "chat":
                    prompt = payload.get("prompt", "")
                    if prompt:
                        def stream_chunk(chunk):
                            ws_manager.broadcast_threadsafe("chat_chunk", {"sender": "Asisten", "text": chunk, "done": False})
                        
                        def process_chat():
                            try:
                                print(f"[WS Chat] Processing prompt: {prompt}")
                                full_resp = gemini_brain.send_prompt_request_stream(prompt, chunk_callback=stream_chunk)
                                print(f"[WS Chat] Finished stream. Response length: {len(full_resp)}")
                                ws_manager.broadcast_threadsafe("chat_chunk", {"sender": "Asisten", "text": "", "done": True, "full_text": full_resp})
                            except Exception as e:
                                print(f"[WS Chat Error] {e}")
                                ws_manager.broadcast_threadsafe("chat_chunk", {"sender": "Asisten", "text": f"Error: {str(e)}", "done": True, "full_text": str(e)})
                        
                        threading.Thread(target=process_chat, daemon=True).start()

                
                elif action == "stt":
                    threading.Thread(target=stt.process_voice_command, daemon=True).start()
                
                elif action == "tts":
                    text = payload.get("text", "")
                    if text:
                        tts.text_to_speech(text)
                
                elif action == "ping":
                    await ws_manager.send_personal_message({"event": "pong"}, websocket)
                    
            except Exception as e:
                await ws_manager.send_personal_message({"event": "error", "data": str(e)}, websocket)
                
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
