import threading
import speech_recognition as sr
import gemini_brain
import tts
from settings_manager import settings_manager
from ws_manager import ws_manager

def speech_to_text(language=None, timeout=5, phrase_time_limit=30, update_status_callback=None, adjust_duration=0.5):
    """
    Merekam suara dari mikrofon dan mengubahnya menjadi teks menggunakan Google Speech Recognition.
    """
    settings = settings_manager.get_settings()
    language = language or settings.get("language", "id-ID")
    
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 2.0
    recognizer.dynamic_energy_threshold = True
    
    try:
        with sr.Microphone() as source:
            if adjust_duration > 0:
                print(f"\n Menyesuaikan kebisingan sekitar ({adjust_duration} detik)...")
                if update_status_callback:
                    update_status_callback("Menyesuaikan kebisingan...")
                ws_manager.broadcast_threadsafe("stt_status", {"status": "adjusting_noise"})
                recognizer.adjust_for_ambient_noise(source, duration=adjust_duration)
            
            print("\n[STT] Mulai Berbicara Sekarang...")
            if update_status_callback:
                update_status_callback("Silakan Berbicara...")
            ws_manager.broadcast_threadsafe("stt_status", {"status": "listening"})
            
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            print("Processing: Sedang mengenali suara Anda...")
            if update_status_callback:
                update_status_callback("Memproses suara...")

            ws_manager.broadcast_threadsafe("stt_status", {"status": "processing"})

            text = recognizer.recognize_google(audio, language=language)
            ws_manager.broadcast_threadsafe("stt_status", {"status": "recognized", "text": text})
            return text

    except sr.WaitTimeoutError:
        print("\n[STT] Waktu tunggu habis. Anda tidak berbicara.")
        if update_status_callback:
            update_status_callback("Waktu habis.")
        ws_manager.broadcast_threadsafe("stt_status", {"status": "error", "error": "timeout"})
        return None
    except sr.UnknownValueError:
        print("\n[STT] Sistem tidak dapat memahami apa yang Anda katakan (suara kurang jelas).")
        if update_status_callback:
            update_status_callback("Suara tidak jelas.")
        ws_manager.broadcast_threadsafe("stt_status", {"status": "error", "error": "unknown_speech"})
        return None
    except sr.RequestError as e:
        print(f"\n[STT] Gagal terhubung ke layanan pengenalan suara: {e}")
        if update_status_callback:
            update_status_callback("Error koneksi STT.")
        ws_manager.broadcast_threadsafe("stt_status", {"status": "error", "error": f"request_error: {str(e)}"})
        return None
    except Exception as e:
        print(f"\n[STT] Terjadi kesalahan tidak terduga: {e}")
        if update_status_callback:
            update_status_callback(f"Error: {str(e)}")
        ws_manager.broadcast_threadsafe("stt_status", {"status": "error", "error": str(e)})
        return None

def process_voice_command(update_gui_callback=None, update_status_callback=None, adjust_duration=0.5, enable_tts=True, tts_rate=150):
    """
    Mengambil input suara, mengirim ke Gemini, memperbarui status, dan menyuarakan jawaban (TTS).
    """
    prompt_text = speech_to_text(update_status_callback=update_status_callback, adjust_duration=adjust_duration)
    if not prompt_text:
        return None
    
    if update_gui_callback:
        update_gui_callback("Anda", prompt_text)
        
    if update_status_callback:
        update_status_callback("🤖 Berpikir...")
    
    # Broadcast status streaming ke WebSocket
    ws_manager.broadcast_threadsafe("chat_stream", {"sender": "Anda", "text": prompt_text, "done": True})
    
    def on_gemini_chunk(chunk):
        ws_manager.broadcast_threadsafe("chat_chunk", {"sender": "Asisten", "text": chunk, "done": False})
        
    response_text = gemini_brain.send_prompt_request_stream(prompt_text, chunk_callback=on_gemini_chunk)
    ws_manager.broadcast_threadsafe("chat_chunk", {"sender": "Asisten", "text": "", "done": True, "full_text": response_text})
    
    if update_gui_callback:
        update_gui_callback("Asisten", response_text)
        
    tts_settings = settings_manager.get_settings().get("tts", {})
    if enable_tts and tts_settings.get("enabled", True) and response_text:
        if update_status_callback:
            update_status_callback("🔊 Membacakan respon...")
        try:
            tts.text_to_speech(response_text, rate=tts_rate, language="id")
        except Exception as e:
            print(f"[TTS Error] {e}")
            
    return response_text

if __name__ == "__main__":
    print("=== PROGRAM INTEGRASI SUARA & GEMINI ===")
    hasil = process_voice_command(
        update_gui_callback=lambda sender, msg: print(f"\n[{sender}]: {msg}"),
        update_status_callback=lambda status: print(f"[Status]: {status}")
    )
