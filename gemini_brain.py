import os
import threading
from dotenv import load_dotenv
import google.generativeai as genai
from settings_manager import settings_manager

load_dotenv()

api_key = os.getenv("GOOGLE_AI_STUDIO_API_KEY")
if not api_key:
    print("[Warning] GOOGLE_AI_STUDIO_API_KEY tidak ditemukan di .env!")

if api_key:
    genai.configure(api_key=api_key)

chat_session = None
_brain_lock = threading.Lock()

def get_configured_model():
    """Membuat objek GenerativeModel menggunakan model yang dikonfigurasi di settings.json."""
    settings = settings_manager.get_settings()
    model_name = settings.get("ai_model", os.getenv("AI_MODEL_KEY", "gemini-1.5-flash"))
    return genai.GenerativeModel(model_name)

def init_chat_session():
    global chat_session
    try:
        model = get_configured_model()
        chat_session = model.start_chat(history=[])
        print(f"[Gemini] Sesi chat diinisialisasi dengan model: {model.model_name}")
    except Exception as e:
        print(f"[Gemini Init Error] {e}")
        chat_session = None

init_chat_session()

def send_prompt_request(prompt_text: str) -> str:
    """Mengirimkan prompt ke Gemini dan mengembalikan respon lengkap."""
    global chat_session
    with _brain_lock:
        if chat_session is None:
            init_chat_session()
        
        if chat_session is None:
            return "Maaf, API Key atau koneksi Gemini belum terkonfigurasi dengan benar."
            
        try:
            response = chat_session.send_message(prompt_text)
            return response.text
        except Exception as e:
            print(f"[Gemini Error] {e}")
            return f"Maaf, sistem mengalami gangguan: {str(e)}"

def send_prompt_request_stream(prompt_text: str, chunk_callback=None) -> str:
    """
    Mengirimkan prompt ke Gemini dan melakukan streaming respon chunk demi chunk
    menggunakan chunk_callback(chunk_text).
    """
    global chat_session
    with _brain_lock:
        if chat_session is None:
            init_chat_session()

        if chat_session is None:
            err_msg = "Maaf, API Key atau koneksi Gemini belum terkonfigurasi dengan benar."
            if chunk_callback:
                chunk_callback(err_msg)
            return err_msg

        try:
            response = chat_session.send_message(prompt_text, stream=True)
            full_text = ""
            for chunk in response:
                chunk_text = ""
                try:
                    if chunk.text:
                        chunk_text = chunk.text
                except Exception:
                    pass
                
                if chunk_text:
                    full_text += chunk_text
                    if chunk_callback:
                        chunk_callback(chunk_text)
            return full_text
        except Exception as e:
            print(f"[Gemini Stream Error] {e}")
            err_msg = f"Maaf, terjadi kesalahan saat streaming: {str(e)}"
            if chunk_callback:
                chunk_callback(err_msg)
            return err_msg

def reset_chat_session():
    """Mereset session chat dengan membuat objek session baru."""
    with _brain_lock:
        init_chat_session()