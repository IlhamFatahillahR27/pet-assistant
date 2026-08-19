import time
import threading
import speech_recognition as sr
from settings_manager import settings_manager
from ws_manager import ws_manager

# Filter & redam traceback internal PortAudio stream close di terminal
def _custom_threading_excepthook(args):
    exc_str = str(args.exc_value)
    if issubclass(args.exc_type, OSError) and any(err in exc_str for err in ["-9988", "-9999", "Stream closed", "device unavailable"]):
        return
    threading.__excepthook__(args)

threading.excepthook = _custom_threading_excepthook

class WakeWordListener:
    def __init__(self, callback=None, threshold=None):
        self.callback = callback
        settings = settings_manager.get_settings().get("wake_word", {})
        self.threshold = threshold if threshold is not None else settings.get("threshold", 0.5)
        self.is_running = False
        self.thread = None
        self.stop_sr_background = None
        self.last_trigger_time = 0
        self.cooldown_seconds = 3.0
        self._lock = threading.Lock()

    def start(self):
        """Menjalankan pendengar Cat-Themed Wake Word di background thread."""
        with self._lock:
            if self.is_running and self.stop_sr_background is not None:
                return
            self.is_running = True

        self.thread = threading.Thread(target=self._run_listener, daemon=True)
        self.thread.start()
        print("[WakeWord] Listener Cat-Themed Wake Word dimulai.")

    def stop(self):
        """Menghentikan pendengar wake word dan membebaskan mikrofon sepenuhnya."""
        with self._lock:
            self.is_running = False

        if self.stop_sr_background:
            try:
                self.stop_sr_background(wait_for_stop=False)
            except Exception:
                pass
            self.stop_sr_background = None

        print("[WakeWord] Listener dihentikan & mikrofon dibebaskan.")

    def _trigger_detected(self, trigger_name, score=1.0):
        """Helper internal untuk memicu event saat kata pemicu terdeteksi."""
        current_time = time.time()
        if current_time - self.last_trigger_time < self.cooldown_seconds:
            return

        self.last_trigger_time = current_time
        print(f"\n[WakeWord] DETEKSI! Kata Pemicu: '{trigger_name}' (Skor: {score:.2f})")

        # Hentikan listener secara menyeluruh agar state is_running kembali False
        self.stop()

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
        recognizer.pause_threshold = 0.6
        recognizer.dynamic_energy_threshold = False

        microphone = None
        for attempt in range(5):
            if not self.is_running:
                return
            try:
                microphone = sr.Microphone()
                with microphone as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    recognizer.energy_threshold = max(220, recognizer.energy_threshold)
                break
            except Exception as e:
                print(f"[WakeWord Init] Menunggu mikrofon ({attempt+1}/5)... {e}")
                time.sleep(0.4)

        if not microphone or not self.is_running:
            self.is_running = False
            return

        print("[WakeWord Engine] Mikrofon aktif. Mendengarkan kata pemicu ('Hi Kitty', 'Hey Kitty', 'Kitty', 'Mew Mew')...")

        def sr_callback(rec, audio):
            if not self.is_running:
                return
            try:
                try:
                    text = rec.recognize_google(audio, language="en-US").lower()
                except Exception:
                    text = rec.recognize_google(audio, language="id-ID").lower()
            except Exception:
                return

            matched_trigger = None
            if any(k in text for k in ["hi kitty", "hai kitty", "hi kiti", "hai kiti", "halo kitty"]):
                matched_trigger = "Hi Kitty"
            elif any(k in text for k in ["hey kitty", "hei kitty", "hey kiti", "hei kiti", "kitty", "kiti"]):
                matched_trigger = "Hey Kitty"
            elif any(k in text for k in ["mew mew", "meow", "mew", "mio", "miu"]):
                matched_trigger = "Mew Mew"

            if matched_trigger:
                self._trigger_detected(matched_trigger, score=0.95)

        try:
            self.stop_sr_background = recognizer.listen_in_background(microphone, sr_callback, phrase_time_limit=3)
        except Exception as e:
            print(f"[WakeWord Background Error] {e}")
            self.is_running = False

# Global listener instance manager
_global_wake_word_listener = None
_wake_lock = threading.Lock()

def get_wake_word_listener():
    global _global_wake_word_listener
    return _global_wake_word_listener

def start_global_wake_word_listener(callback=None):
    global _global_wake_word_listener
    with _wake_lock:
        if _global_wake_word_listener and _global_wake_word_listener.is_running and _global_wake_word_listener.stop_sr_background is not None:
            return _global_wake_word_listener
        if _global_wake_word_listener:
            _global_wake_word_listener.stop()
        _global_wake_word_listener = WakeWordListener(callback=callback)
        _global_wake_word_listener.start()
        return _global_wake_word_listener

def stop_global_wake_word_listener():
    global _global_wake_word_listener
    with _wake_lock:
        if _global_wake_word_listener:
            _global_wake_word_listener.stop()
            _global_wake_word_listener = None
