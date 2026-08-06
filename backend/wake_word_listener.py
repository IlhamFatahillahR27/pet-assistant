import time
import threading
import speech_recognition as sr
from settings_manager import settings_manager
from ws_manager import ws_manager

# Filter & redam traceback internal PortAudio stream close di terminal
def _custom_threading_excepthook(args):
    exc_str = str(args.exc_value)
    if issubclass(args.exc_type, OSError) and any(err in exc_str for err in ["-9988", "-9999", "Stream closed"]):
        return
    threading.__excepthook__(args)

threading.excepthook = _custom_threading_excepthook

class WakeWordListener:
    def __init__(self, callback=None, target_models=None, threshold=None):
        """
        :param callback: Fungsi callback opsional saat wake word terdeteksi
        """
        self.callback = callback
        settings = settings_manager.get_settings().get("wake_word", {})
        self.cat_keywords = settings.get("cat_keywords", ["hi kitty", "mew mew", "hey kitty"])
        self.threshold = threshold if threshold is not None else settings.get("threshold", 0.5)
        self.is_running = False
        self.thread = None
        self.stop_sr_background = None
        self.last_trigger_time = 0
        self.cooldown_seconds = 2.0

    def start(self):
        """Menjalankan pendengar Cat-Themed Wake Word di background thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run_listener, daemon=True)
        self.thread.start()
        print("[WakeWord] Listener Cat-Themed Wake Word berhasil dimulai.")

    def stop(self):
        """Menghentikan pendengar wake word dan membebaskan mikrofon."""
        self.is_running = False
        
        if self.stop_sr_background:
            try:
                # Menghentikan background listener tanpa mencetak traceback PortAudio
                self.stop_sr_background(wait_for_stop=False)
            except Exception:
                pass
            self.stop_sr_background = None
            time.sleep(0.4)

        print("[WakeWord] Listener dihentikan & mikrofon dibebaskan.")

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

    def _run_listener(self):
        """Membuka mikrofon secara bersih dan mendengarkan frasa kata pemicu kucing."""
        recognizer = sr.Recognizer()
        recognizer.pause_threshold = 0.7
        recognizer.dynamic_energy_threshold = False
        
        try:
            microphone = sr.Microphone()
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.3)
                recognizer.energy_threshold = max(250, recognizer.energy_threshold)
            
            print(f"[WakeWord Engine] Mikrofon aktif. Mendengarkan: {self.cat_keywords}...")

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

                # Periksa kata pemicu kucing
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
        except Exception as e:
            print(f"[WakeWord Initialization Error] Gagal membuka mikrofon: {e}")

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
