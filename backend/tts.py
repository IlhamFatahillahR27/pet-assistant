import pyttsx3
import winreg
import threading
from settings_manager import settings_manager
from ws_manager import ws_manager

_tts_lock = threading.Lock()

def get_available_voices():
    """
    Mendapatkan semua daftar suara (SAPI5 standar & Windows OneCore) yang terinstall di sistem.
    """
    voices_list = []
    
    # 1. pyttsx3 standar (SAPI5)
    try:
        engine = pyttsx3.init()
        for v in engine.getProperty('voices'):
            voices_list.append({
                'id': v.id,
                'name': v.name
            })
    except Exception:
        pass
        
    # 2. Windows OneCore Registry
    onecore_path = r"SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens"
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, onecore_path)
        for i in range(winreg.QueryInfoKey(key)[0]):
            sub_key_name = winreg.EnumKey(key, i)
            full_subkey_path = f"{onecore_path}\\{sub_key_name}"
            
            sub_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, full_subkey_path)
            try:
                display_name, _ = winreg.QueryValueEx(sub_key, "")
            except Exception:
                display_name = sub_key_name
            
            voice_id = f"HKEY_LOCAL_MACHINE\\{full_subkey_path}"
            
            if not any(v['id'] == voice_id for v in voices_list):
                voices_list.append({
                    'id': voice_id,
                    'name': display_name
                })
    except OSError:
        pass
        
    return voices_list

import re

def clean_text_for_speech(text: str) -> str:
    """Membersihkan simbol markdown, emoji, dan karakter khusus agar pyttsx3 membaca teks sampai selesai."""
    if not text:
        return ""
    # Hapus simbol markdown (*, #, $, `, _, ~)
    clean = re.sub(r'[\*\#\`\$\_\~]', ' ', text)
    # Normalkan spasi berlebih dan pemisah baris
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def text_to_speech(text: str, rate: int = None, volume: float = None, language: str = None, status_callback=None):
    """
    Mengubah teks menjadi suara menggunakan pyttsx3. Thread-safe dengan _tts_lock.
    """
    settings = settings_manager.get_settings().get("tts", {})
    if not settings.get("enabled", True):
        print("[TTS] Fitur TTS sedang dinonaktifkan di pengaturan.")
        return

    text_clean = clean_text_for_speech(text)
    if not text_clean:
        return

    rate = rate if rate is not None else settings.get("rate", 160)
    volume = volume if volume is not None else settings.get("volume", 1.0)
    language = language if language is not None else settings.get("language", "id")

    def _speak():
        with _tts_lock:
            com_initialized = False
            try:
                try:
                    import pythoncom
                    pythoncom.CoInitialize()
                    com_initialized = True
                except Exception:
                    pass

                if status_callback:
                    status_callback("speaking")
                ws_manager.broadcast_threadsafe("tts_status", {"status": "speaking", "text": text_clean})

                engine = pyttsx3.init()
                engine.setProperty('rate', rate)
                engine.setProperty('volume', volume)

                voices = get_available_voices()
                selected_voice = None
                
                for voice in voices:
                    name_lower = voice['name'].lower()
                    id_lower = voice['id'].lower()
                    if language.lower() == "id":
                        if "indonesia" in name_lower or "id_id" in id_lower or "id-id" in id_lower:
                            selected_voice = voice
                            break
                    else:
                        if language.lower() in name_lower or language.lower() in id_lower:
                            selected_voice = voice
                            break

                if selected_voice:
                    engine.setProperty('voice', selected_voice['id'])
                else:
                    default_voices = engine.getProperty('voices')
                    if default_voices:
                        engine.setProperty('voice', default_voices[0].id)

                engine.say(text_clean)
                engine.runAndWait()
                engine.stop()

                if status_callback:
                    status_callback("finished")
                ws_manager.broadcast_threadsafe("tts_status", {"status": "finished"})

            except Exception as e:
                print(f"[TTS Error] {e}")
                if status_callback:
                    status_callback(f"error: {str(e)}")
                ws_manager.broadcast_threadsafe("tts_status", {"status": "error", "error": str(e)})
            finally:
                if com_initialized:
                    try:
                        import pythoncom
                        pythoncom.CoUninitialize()
                    except Exception:
                        pass

    # Jalankan TTS di thread non-daemon agar Windows SAPI5 audio buffer tidak terhenti di tengah jalan
    threading.Thread(target=_speak, daemon=False).start()

if __name__ == "__main__":
    teks = input("Masukkan teks yang ingin dibacakan: ")
    text_to_speech(teks, rate=160, volume=0.9, language="id")
