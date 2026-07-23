import os
from dotenv import load_dotenv
import google.generativeai as genai

# Memuat variabel dari file .env
load_dotenv()

# 1. Mengambil API Key dari .env
api_key = os.getenv("GOOGLE_AI_STUDIO_API_KEY")
model_env = os.getenv("AI_MODEL_KEY")
if not api_key:
    raise ValueError("API Key tidak ditemukan! Pastikan GOOGLE_AI_STUDIO_API_KEY sudah diset di file .env")

genai.configure(api_key=api_key)

# 2. Panggil model Gemini (Ketik 'gemini-pro' untuk model berbasis teks)
model = genai.GenerativeModel(model_env)

# Simpan session chat secara global
chat_session = None

def init_chat_session():
    global chat_session
    chat_session = model.start_chat(history=[])

# Inisialisasi awal saat modul di-import
init_chat_session()

# 3. Buat fungsi untuk mengirimkan prompt/pertanyaan
def send_prompt_request(prompt_text):
    global chat_session
    if chat_session is None:
        init_chat_session()
    try:
        # Mengirimkan pertanyaan ke Gemini dalam sesi chat yang sedang berjalan
        response = chat_session.send_message(prompt_text)
        # Mengembalikan teks jawaban dari Gemini (disimpan di response.text)
        return response.text
    except Exception as e:
        return f"Maaf, sistem mengalami gangguan: {str(e)}"

def reset_chat_session():
    """Mereset session chat dengan membuat objek session baru."""
    init_chat_session()