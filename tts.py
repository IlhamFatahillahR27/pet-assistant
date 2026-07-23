import pyttsx3
import winreg

def get_available_voices():
    """
    Mendapatkan semua daftar suara (SAPI5 standar & Windows OneCore) yang terinstall di sistem.
    """
    voices_list = []
    
    # 1. Coba ambil dari pyttsx3 standar (SAPI5)
    try:
        engine = pyttsx3.init()
        for v in engine.getProperty('voices'):
            voices_list.append({
                'id': v.id,
                'name': v.name
            })
    except Exception:
        pass
        
    # 2. Coba ambil dari Windows OneCore Registry (Sering dipakai Windows 10/11 untuk suara baru)
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
            
            # Hindari duplikasi jika sudah terdaftar
            if not any(v['id'] == voice_id for v in voices_list):
                voices_list.append({
                    'id': voice_id,
                    'name': display_name
                })
    except OSError:
        pass
        
    return voices_list

def text_to_speech(text, rate=150, volume=1.0, language="id"):
    """
    Mengubah teks menjadi suara menggunakan pyttsx3 dengan dukungan multi-platform registry.
    """
    try:
        engine = pyttsx3.init()

        # Atur parameter
        engine.setProperty('rate', rate)
        engine.setProperty('volume', volume)

        # Cari suara terbaik yang cocok dengan filter bahasa
        voices = get_available_voices()
        selected_voice = None
        
        # Cari suara yang mengandung kata kunci bahasa (misal 'id' atau 'indonesia')
        for voice in voices:
            name_lower = voice['name'].lower()
            id_lower = voice['id'].lower()
            
            # Pencarian spesifik bahasa indonesia
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
            print(f"Menggunakan suara: {selected_voice['name']}")
        else:
            print(f"\n[Peringatan] Suara untuk bahasa '{language}' tidak ditemukan di Windows Anda.")
            print("=> Pastikan Anda sudah mengunduh suara Bahasa Indonesia di Settings Windows Anda.")
            # Default ke suara pertama yang tersedia jika gagal menemukan
            default_voices = engine.getProperty('voices')
            if default_voices:
                engine.setProperty('voice', default_voices[0].id)
                print(f"Menggunakan suara default: {default_voices[0].name}")

        # Jalankan pembacaan teks
        engine.say(text)
        engine.runAndWait()

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    teks = input("Masukkan teks yang ingin dibacakan: ")
    text_to_speech(teks, rate=160, volume=0.9, language="id")
