"""
gemini_brain.py
Wrapper modul AI untuk kompatibilitas mundur dengan STT dan modul lama.
Seluruh logika inti multi-model sekarang dikelola oleh ai_brain.py.
"""

from ai_brain import (
    ai_brain,
    DEFAULT_SYSTEM_INSTRUCTION as CAT_ASSISTANT_SYSTEM_INSTRUCTION,
    SUPPORTED_PROVIDERS
)

def send_prompt_request(prompt_text: str) -> str:
    """Mengirimkan prompt ke provider AI aktif dan mengembalikan respon lengkap."""
    return ai_brain.send_prompt_request(prompt_text)

def send_prompt_request_stream(prompt_text: str, chunk_callback=None) -> str:
    """Mengirimkan prompt ke provider AI aktif dan melakukan streaming respon chunk demi chunk."""
    return ai_brain.send_prompt_request_stream(prompt_text, chunk_callback=chunk_callback)

def reset_chat_session():
    """Mereset session chat aktif."""
    ai_brain.reset_chat_session()