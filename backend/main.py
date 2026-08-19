import asyncio
import threading
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from settings_manager import settings_manager
from user_memory import user_memory_manager
from ws_manager import ws_manager
from ai_brain import ai_brain, SUPPORTED_PROVIDERS
import stt
import tts
import wake_word_listener

# Filter & redam traceback internal PortAudio stream close di terminal
def _custom_threading_excepthook(args):
    exc_str = str(args.exc_value)
    if issubclass(args.exc_type, OSError) and any(err in exc_str for err in ["-9988", "-9999", "Stream closed"]):
        return
    threading.__excepthook__(args)

threading.excepthook = _custom_threading_excepthook

app = FastAPI(
    title="Pet Assistant Backend API",
    description="FastAPI & WebSocket Server untuk Pet Assistant Multi-Model AI",
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
    
    # Auto-start Wake Word Listener secara asinkron agar tidak memblokir Uvicorn startup
    settings = settings_manager.get_settings().get("wake_word", {})
    if settings.get("enabled", True):
        def async_start_listener():
            import time
            time.sleep(1.0)
            try:
                wake_word_listener.start_global_wake_word_listener()
                print("[Startup] Wake Word Listener berhasil dimulai dan aktif mendengarkan.")
            except Exception as e:
                print(f"[Startup Warning] Gagal memulai Wake Word listener: {e}")

        threading.Thread(target=async_start_listener, daemon=True).start()

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
    voice_id: Optional[str] = None

class SettingsUpdateRequest(BaseModel):
    selected_cat: Optional[str] = None
    theme: Optional[str] = None
    ai_provider_config: Optional[Dict[str, Any]] = None
    language: Optional[str] = None
    tts: Optional[Dict[str, Any]] = None
    wake_word: Optional[Dict[str, Any]] = None

class MemoryCreateRequest(BaseModel):
    fact: str
    category: Optional[str] = "general"

class UrlRequest(BaseModel):
    url: str

class AITestRequest(BaseModel):
    provider: str
    model: Optional[str] = ""
    api_key: Optional[str] = ""
    base_url: Optional[str] = ""


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

# AI Provider Endpoints
@app.get("/api/ai/providers", tags=["AI Model Switcher"])
def get_ai_providers():
    """Mengembalikan daftar provider AI, model, dan status konfigurasi."""
    return {"providers": list(SUPPORTED_PROVIDERS.values())}

@app.post("/api/ai/test", tags=["AI Model Switcher"])
def test_ai_connection(req: AITestRequest):
    """Mengetes kredensial / koneksi ke provider AI."""
    result = ai_brain.test_provider_connection(
        provider_id=req.provider,
        model_id=req.model or "",
        api_key=req.api_key or "",
        base_url=req.base_url or ""
    )
    return result

@app.get("/api/ai/ollama/models", tags=["AI Model Switcher"])
def get_ollama_models(base_url: Optional[str] = "http://localhost:11434"):
    """Mengambil daftar model AI yang sudah terinstall di Ollama lokal."""
    models = ai_brain.fetch_ollama_local_models(base_url=base_url)
    return {"models": models}

# System & OS Settings Endpoints
@app.post("/api/system/open-speech-settings", tags=["System"])
def open_speech_settings():
    """Membuka jendela Windows Speech Settings secara native (ms-settings:speech)."""
    import os
    try:
        os.system("start ms-settings:speech")
        return {"status": "opened", "message": "Windows Speech Settings dibuka"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuka settings: {e}")

@app.post("/api/system/open-browser", tags=["System"])
def open_browser(req: UrlRequest):
    """Membuka URL di browser bawaan sistem secara otomatis."""
    import webbrowser
    try:
        webbrowser.open(req.url)
        return {"status": "opened", "url": req.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuka browser: {e}")

# Memory Endpoints
@app.get("/api/memories", tags=["Memory"])
def get_memories():
    return {"memories": user_memory_manager.get_all_memories()}

@app.post("/api/memories", tags=["Memory"])
async def add_memory(req: MemoryCreateRequest):
    if not req.fact.strip():
        raise HTTPException(status_code=400, detail="Fakta memori tidak boleh kosong")
    
    new_mem = user_memory_manager.add_memory(req.fact, req.category or "general")
    all_mems = user_memory_manager.get_all_memories()
    await ws_manager.broadcast("memory_updated", all_mems)
    return {"status": "success", "memory": new_mem, "memories": all_mems}

@app.delete("/api/memories/{memory_id}", tags=["Memory"])
async def delete_memory(memory_id: str):
    success = user_memory_manager.delete_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memori tidak ditemukan")
    all_mems = user_memory_manager.get_all_memories()
    await ws_manager.broadcast("memory_updated", all_mems)
    return {"status": "deleted", "memory_id": memory_id, "memories": all_mems}

@app.delete("/api/memories", tags=["Memory"])
async def clear_all_memories():
    user_memory_manager.clear_all_memories()
    all_mems = user_memory_manager.get_all_memories()
    await ws_manager.broadcast("memory_updated", all_mems)
    return {"status": "cleared", "memories": []}

@app.post("/api/chat", tags=["AI Chat"])
async def chat_with_ai(req: ChatRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt tidak boleh kosong")
    
    response_text = ai_brain.send_prompt_request(req.prompt)
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
        language=req.language,
        voice_id=req.voice_id
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

@app.post("/api/system/shutdown", tags=["System"])
def shutdown_system():
    """Menghentikan backend server dan membebaskan seluruh resource audio."""
    wake_word_listener.stop_global_wake_word_listener()
    def kill_proc():
        import time, os, signal
        time.sleep(0.3)
        os.kill(os.getpid(), signal.SIGTERM)
    threading.Thread(target=kill_proc, daemon=True).start()
    return {"status": "shutting_down", "message": "Server sedang dihentikan"}

# WebSocket Endpoint

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    # Kirim status koneksi, settings, dan memories saat ini ke client baru
    await ws_manager.send_personal_message(
        {
            "event": "connected",
            "data": {
                "message": "Terhubung ke Pet Assistant WebSocket Server",
                "settings": settings_manager.get_settings(),
                "memories": user_memory_manager.get_all_memories()
            }
        },
        websocket
    )

    # Pastikan wake word listener menyala saat frontend terhubung
    ww_settings = settings_manager.get_settings().get("wake_word", {})
    if ww_settings.get("enabled", True):
        wake_word_listener.start_global_wake_word_listener()
    
    try:
        while True:
            data_str = await websocket.receive_text()
            try:
                payload = json.loads(data_str)
                action = payload.get("action")
                
                if action == "chat":
                    prompt = payload.get("prompt", "")
                    if prompt:
                        def process_chat():
                            try:
                                print(f"[WS Chat] Processing prompt: {prompt}")
                                def stream_chunk(chunk):
                                    ws_manager.broadcast_threadsafe("chat_chunk", {"sender": "Asisten", "text": chunk, "done": False})
                                
                                # 1. Hasilkan jawaban dengan streaming teks langsung ke chat UI secara real-time
                                full_resp = ai_brain.send_prompt_request_stream(prompt, chunk_callback=stream_chunk)
                                # 2. Tampilkan teks lengkap instan di UI
                                ws_manager.broadcast_threadsafe("chat_chunk", {"sender": "Asisten", "text": "", "done": True, "full_text": full_resp})
                                
                                # 3. Putar audio WAV secara paralel di background
                                tts_settings = settings_manager.get_settings().get("tts", {})
                                if tts_settings.get("enabled", True) and full_resp:
                                    def async_speak():
                                        rate = tts_settings.get("rate", 160)
                                        volume = tts_settings.get("volume", 1.0)
                                        voice_id = tts_settings.get("voice_id", "")
                                        tts.text_to_speech(full_resp, rate=rate, volume=volume, voice_id=voice_id, sync=True)
                                    
                                    threading.Thread(target=async_speak, daemon=True).start()
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
                
                elif action == "reset_session":
                    ai_brain.reset_chat_session()
                    await ws_manager.send_personal_message({"event": "session_reset", "data": "Chat session reset"}, websocket)

                elif action == "ping":
                    await ws_manager.send_personal_message({"event": "pong"}, websocket)
                    
            except Exception as e:
                await ws_manager.send_personal_message({"event": "error", "data": str(e)}, websocket)
                
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
