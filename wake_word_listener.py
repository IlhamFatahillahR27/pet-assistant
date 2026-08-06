import time
import threading
import numpy as np
import pyaudio
import speech_recognition as sr
import openwakeword
from openwakeword.model import Model
from settings_manager import settings_manager
from ws_manager import ws_manager

class WakeWordListener:
    def __init__(self, callback=None, target_models=None, threshold=None):
        """
        :param callback: Fungsi callback opsional saat wake word terdeteksi
        :param target_models: List kata pemicu (misal ['hey_jarvis', 'alexa'])
        :param threshold: Ambang batas keyakinan deteksi (0.0 - 1.0)
        """
        self.callback = callback
        settings = settings_manager.get_settings().get("wake_word", {})
        self.target_models = target_models or settings.get("target_models", ['hey_jarvis', 'alexa'])
        self.cat_keywords = settings.get("cat_keywords", ["hi kitty", "mew mew", "hey kitty"])
        self.threshold = threshold if threshold is not None else settings.get("threshold", 0.5)
        self.is_running = False
        self.thread = None
        self.pyaudio_instance = None
        self.stream = None
        self.oww_model = None
        self.stop_sr_background = None
        self.last_trigger_time = 0
        self.cooldown_seconds = 2.0

    def start(self):
        """Menjalankan pendengar wake word (Hybrid OpenWakeWord + Cat Keyword Spotter) di background thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        
        # Mulai juga pendengar frasa kata kucing ("Hi Kitty", "Mew Mew", "Hey Kitty")
        self._start_sr_keyword_listener()
        print("[WakeWord] Listener Cat-Themed Wake Word berhasil dimulai.")

    def stop(self):
        """Menghentikan pendengar wake word."""
        self.is_running = False
        
        # Hentikan background listener SpeechRecognition jika ada
        if self.stop_sr_background:
            try:
                self.stop_sr_background(wait_for_stop=False)
            except Exception:
                pass
            self.stop_sr_background = None

        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass
        if self.pyaudio_instance:
            try:
                self.pyaudio_instance.terminate()
            except Exception:
                pass
        print("[WakeWord] Listener dihentikan.")

    def _trigger_detected(self, trigger_name, score=1.0):
        """Helper internal untuk memicu event saat kata pemicu terdeteksi."""
        current_time = time.time()
        if current_time - self.last_trigger_time > self.cooldown_seconds:
            self.last_trigger_time = current_time
            print(f"\n[WakeWord] DETEKSI! Kata Pemicu Kucing: '{trigger_name}' (Skor: {score:.2f})")
            
            # Callback lokal jika ada
            if self.callback:
                self.callback(trigger_name)
            
            # Broadcast via WebSocket ke seluruh client terhubung
            ws_manager.broadcast_threadsafe(
                "wakeword_detected",
                {"model": trigger_name, "score": float(score)}
            )

    def _start_sr_keyword_listener(self):
        """Pendengar frasa percakapan langsung untuk frasa 'Hi Kitty', 'Mew Mew', 'Hey Kitty'."""
        def sr_worker():
            recognizer = sr.Recognizer()
            recognizer.pause_threshold = 0.8
            recognizer.dynamic_energy_threshold = True
            
            try:
                microphone = sr.Microphone()
                with microphone as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                def sr_callback(rec, audio):
                    if not self.is_running:
                        return
                    try:
                        # Coba pengenalan suara Bahasa Inggris & Indonesia
                        try:
                            text = rec.recognize_google(audio, language="en-US").lower()
                        except Exception:
                            text = rec.recognize_google(audio, language="id-ID").lower()
                    except Exception:
                        return

                    # Periksa apakah kalimat mengandung kata pemicu kucing
                    matched_trigger = None
                    if "hi kitty" in text or "hai kitty" in text or "hi kiti" in text:
                        matched_trigger = "Hi Kitty"
                    elif "hey kitty" in text or "hei kitty" in text or "hey kiti" in text or "kitty" in text or "kiti" in text:
                        matched_trigger = "Hey Kitty"
                    elif "mew mew" in text or "mew" in text or "meow" in text or "mio" in text or "miu" in text:
                        matched_trigger = "Mew Mew"

                    if matched_trigger:
                        self._trigger_detected(matched_trigger, score=0.95)

                self.stop_sr_background = recognizer.listen_in_background(microphone, sr_callback, phrase_time_limit=3)
                print("[Keyword Spotter] Pendengar frasa kucing (Hi Kitty / Mew Mew / Hey Kitty) aktif.")
            except Exception as e:
                print(f"[Keyword Spotter Error] {e}")

        threading.Thread(target=sr_worker, daemon=True).start()

    def _listen_loop(self):
        CHUNK = 1280  # 80ms chunk pada sampel rate 16000 Hz
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        try:
            openwakeword.utils.download_models()
            self.oww_model = Model(wakeword_models=self.target_models, inference_framework="onnx")
            
            self.pyaudio_instance = pyaudio.PyAudio()
            self.stream = self.pyaudio_instance.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )

            print(f"[WakeWord Engine] Mendengarkan pemicu suara kucing...")

            while self.is_running:
                try:
                    data = self.stream.read(CHUNK, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    
                    prediction = self.oww_model.predict(audio_data)

                    for model_name, score in self.oww_model.prediction_buffer.items():
                        current_score = score[-1]
                        if current_score >= self.threshold:
                            # Mapping model bawaan openwakeword ke kata pemicu kucing sebagai fallback
                            display_wakeword = "Hey Kitty"
                            if "jarvis" in model_name.lower():
                                display_wakeword = "Hi Kitty"
                            elif "alexa" in model_name.lower():
                                display_wakeword = "Hey Kitty"
                            else:
                                display_wakeword = "Mew Mew"
                                
                            self._trigger_detected(display_wakeword, score=float(current_score))
                            break
                except Exception as e:
                    if self.is_running:
                        print(f"[WakeWord Loop Error] {e}")
                    time.sleep(0.1)

        except Exception as e:
            print(f"[WakeWord Initialization Error] {e}")
        finally:
            self.stop()

# Global listener instance manager
_global_wake_word_listener = None

def get_wake_word_listener():
    global _global_wake_word_listener
    return _global_wake_word_listener

def start_global_wake_word_listener(callback=None):
    global _global_wake_word_listener
    if _global_wake_word_listener and _global_wake_word_listener.is_running:
        return _global_wake_word_listener
    _global_wake_word_listener = WakeWordListener(callback=callback)
    _global_wake_word_listener.start()
    return _global_wake_word_listener

def stop_global_wake_word_listener():
    global _global_wake_word_listener
    if _global_wake_word_listener:
        _global_wake_word_listener.stop()
        _global_wake_word_listener = None

if __name__ == "__main__":
    def on_detected(model_name):
        print(f"[WAKE WORD DETECTED] [{model_name}]")

    listener = WakeWordListener(callback=on_detected)

    listener.start()
    
    print("Mendengarkan 'Hi Kitty', 'Mew Mew', 'Hey Kitty'... Tekan Ctrl+C untuk keluar...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        listener.stop()
