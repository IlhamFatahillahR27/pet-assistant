import threading
import speech_recognition as sr
import gemini_brain
import tts

def speech_to_text(language="id-ID", timeout=5, phrase_time_limit=30, update_status_callback=None, adjust_duration=0.5):
    """
    Merekam suara dari mikrofon dan mengubahnya menjadi teks menggunakan Google Speech Recognition.
    
    :param language: Kode bahasa target (default 'id-ID' untuk Bahasa Indonesia)
    :param timeout: Durasi tunggu (detik) sebelum mulai berbicara
    :param phrase_time_limit: Durasi maksimal (detik) untuk satu frasa bicara (diperpanjang agar tidak terpotong)
    :param update_status_callback: Callback function untuk memperbarui status di UI
    :param adjust_duration: Durasi penyesuaian kebisingan sekitar (detik), set ke 0 untuk menonaktifkan
    :return: Teks hasil pengenalan suara atau None jika gagal
    """
    # Inisialisasi recognizer
    recognizer = sr.Recognizer()
    
    # Pengaturan agar perekaman tidak cepat berhenti saat pengguna berhenti sejenak / menjelaskan
    recognizer.pause_threshold = 2.0  # Jeda nafas 2 detik sebelum dianggap selesai bicara (default bawaan 0.8s)
    recognizer.dynamic_energy_threshold = True  # Adaptif terhadap kebisingan ruangan
    
    # Gunakan mikrofon default sebagai input audio
    try:
        with sr.Microphone() as source:
            if adjust_duration > 0:
                print(f"\n Menyesuaikan kebisingan sekitar ({adjust_duration} detik)...")
                if update_status_callback:
                    update_status_callback("Menyesuaikan kebisingan...")
                recognizer.adjust_for_ambient_noise(source, duration=adjust_duration)
            
            print("\n[STT] Mulai Berbicara Sekarang...")
            print("===============================================")
            if update_status_callback:
                update_status_callback("🎙️ Silakan Berbicara...")
            
            # Rekam suara
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            print("Processing: Sedang mengenali suara Anda...")
            if update_status_callback:
                update_status_callback("⏳ Memproses suara...")

            # Kenali suara menggunakan Google Speech Recognition
            text = recognizer.recognize_google(audio, language=language)
            return text

    except sr.WaitTimeoutError:
        print("\n[STT] Waktu tunggu habis. Anda tidak berbicara.")
        if update_status_callback:
            update_status_callback("Waktu habis.")
        return None
    except sr.UnknownValueError:
        print("\n[STT] Sistem tidak dapat memahami apa yang Anda katakan (suara kurang jelas).")
        if update_status_callback:
            update_status_callback("Suara tidak jelas.")
        return None
    except sr.RequestError as e:
        print(f"\n[STT] Gagal terhubung ke layanan pengenalan suara: {e}")
        if update_status_callback:
            update_status_callback("Error koneksi STT.")
        return None
    except Exception as e:
        print(f"\n[STT] Terjadi kesalahan tidak terduga: {e}")
        if update_status_callback:
            update_status_callback(f"Error: {str(e)}")
        return None

def process_voice_command(update_gui_callback=None, update_status_callback=None, adjust_duration=0.5, enable_tts=True, tts_rate=150):
    """
    Mengambil input suara, mengirim ke Gemini, memperbarui GUI, dan menyuarakan jawaban (TTS).
    """
    # 1. Dapatkan teks dari suara
    prompt_text = speech_to_text(language="id-ID", update_status_callback=update_status_callback, adjust_duration=adjust_duration)
    if not prompt_text:
        return None
    
    # Update input user di GUI
    if update_gui_callback:
        update_gui_callback("Anda", prompt_text)
        
    # 2. Kirim prompt_text ke fungsi gemini_brain
    if update_status_callback:
        update_status_callback("🤖 Berpikir...")
    
    response_text = gemini_brain.send_prompt_request(prompt_text)
    
    # Update jawaban Gemini di GUI
    if update_gui_callback:
        update_gui_callback("Asisten", response_text)
        
    # 3. Bacakan jawaban menggunakan TTS jika diaktifkan
    if enable_tts and response_text:
        if update_status_callback:
            update_status_callback("🔊 Membacakan respon...")
        try:
            tts.text_to_speech(response_text, rate=tts_rate, language="id")
        except Exception as e:
            print(f"[TTS Error] {e}")
            
    return response_text

if __name__ == "__main__":
    print("=== PROGRAM INTEGRASI SUARA & GEMINI ===")
    print("Pastikan mikrofon Anda terhubung dan aktif.")
    
    hasil = process_voice_command(
        update_gui_callback=lambda sender, msg: print(f"\n[{sender}]: {msg}"),
        update_status_callback=lambda status: print(f"[Status]: {status}")
    )



