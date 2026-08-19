import os
import re
import time
import winreg
import winsound
import threading
import tempfile
import pyttsx3
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

def clean_text_for_speech(text: str) -> str:
    """Membersihkan simbol markdown, emoji, dan karakter khusus agar pyttsx3 membaca teks lancar tanpa terhenti."""
    if not text:
        return ""
    # Hapus URL
    clean = re.sub(r'https?://\S+', '', text)
    # Hapus format markdown (*, #, $, `, _, ~, >, |, -)
    clean = re.sub(r'[\*\#\`\$\_\~\>\|\-\[\]\(\)\{\}\\]', ' ', clean)
    # Hapus karakter emoji / simbol non-huruf selain tanda baca dasar
    clean = re.sub(r'[^\w\s\.,\?!;:\'\"]', ' ', clean)
    # Normalkan spasi berlebih
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def _perform_speak_via_wav(text_clean: str, rate: int, volume: float, language: str, target_voice_id: str, status_callback=None):
    """
    Mensintesis teks ke file WAV sementara lalu memutarnya secara native dengan winsound.
    Setelah selesai diputar, file sementara otomatis dihapus untuk menjaga kebersihan sistem.
    """
    with _tts_lock:
        com_initialized = False
        temp_wav_path = None
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

            # Buat file WAV sementara di direktori temp OS
            fd, temp_wav_path = tempfile.mkstemp(suffix=".wav", prefix="pet_tts_")
            os.close(fd)

            engine = pyttsx3.init()
            engine.setProperty('rate', rate)
            engine.setProperty('volume', volume)

            voices = get_available_voices()
            selected_voice_id = None
            
            # 1. Cari berdasarkan target_voice_id
            if target_voice_id:
                for voice in voices:
                    if voice['id'] == target_voice_id or voice['name'] == target_voice_id:
                        selected_voice_id = voice['id']
                        break
            
            # 2. Fallback berdasarkan bahasa
            if not selected_voice_id:
                for voice in voices:
                    name_lower = voice['name'].lower()
                    id_lower = voice['id'].lower()
                    if language.lower() == "id":
                        if "indonesia" in name_lower or "id_id" in id_lower or "id-id" in id_lower or "andika" in name_lower or "gadis" in name_lower:
                            selected_voice_id = voice['id']
                            break
                    else:
                        if language.lower() in name_lower or language.lower() in id_lower:
                            selected_voice_id = voice['id']
                            break

            if selected_voice_id:
                try:
                    engine.setProperty('voice', selected_voice_id)
                except Exception as ve:
                    print(f"[TTS Voice Warning] Gagal set voice {selected_voice_id}: {ve}")
            else:
                default_voices = engine.getProperty('voices')
                if default_voices:
                    engine.setProperty('voice', default_voices[0].id)

            print(f"[TTS] Mensintesis suara ke WAV ({len(text_clean)} karakter)...")
            # Simpan sintesis suara ke file WAV (tidak mengganggu live audio stream)
            engine.save_to_file(text_clean, temp_wav_path)
            engine.runAndWait()
            engine.stop()

            # Putar audio WAV secara native dan sinkron sampai selesai
            if os.path.exists(temp_wav_path) and os.path.getsize(temp_wav_path) > 100:
                print("[TTS] Memutar suara jawaban...")
                winsound.PlaySound(temp_wav_path, winsound.SND_FILENAME)
                print("[TTS] Selesai memutar suara.")
            else:
                print("[TTS Warning] File audio WAV kosong atau gagal terbentuk.")

            if status_callback:
                status_callback("finished")
            ws_manager.broadcast_threadsafe("tts_status", {"status": "finished"})

        except Exception as e:
            print(f"[TTS Error] {e}")
            if status_callback:
                status_callback(f"error: {str(e)}")
            ws_manager.broadcast_threadsafe("tts_status", {"status": "error", "error": str(e)})
        finally:
            # Hapus file WAV sementara setelah pemutaran selesai
            if temp_wav_path and os.path.exists(temp_wav_path):
                try:
                    os.remove(temp_wav_path)
                    print("[TTS Cleanup] File WAV sementara berhasil dihapus.")
                except Exception:
                    pass

            if com_initialized:
                try:
                    import pythoncom
                    pythoncom.CoUninitialize()
                except Exception:
                    pass

def text_to_speech(text: str, rate: int = None, volume: float = None, language: str = None, voice_id: str = None, status_callback=None, sync: bool = False):
    """
    Mengubah teks menjadi suara menggunakan sintesis file WAV + winsound.
    Jika sync=True, fungsi akan menunggu sampai seluruh pembacaan suara selesai sebelum return.
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
    target_voice_id = voice_id if voice_id is not None else settings.get("voice_id", "")

    if sync:
        _perform_speak_via_wav(text_clean, rate, volume, language, target_voice_id, status_callback)
    else:
        threading.Thread(
            target=_perform_speak_via_wav,
            args=(text_clean, rate, volume, language, target_voice_id, status_callback),
            daemon=False
        ).start()

if __name__ == "__main__":
    teks = input("Masukkan teks yang ingin dibacakan: ")
    text_to_speech(teks, rate=160, volume=0.9, language="id", sync=True)
