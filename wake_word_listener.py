import time
import threading
import numpy as np
import pyaudio
import openwakeword
from openwakeword.model import Model

class WakeWordListener:
    def __init__(self, callback, target_models=None, threshold=0.5):
        """
        :param callback: Fungsi callback yang dipanggil saat wake word terdeteksi
        :param target_models: List kata pemicu, default ['hey_jarvis', 'alexa']
        :param threshold: Ambang batas keyakinan deteksi (0.0 - 1.0)
        """
        self.callback = callback
        self.target_models = target_models or ['hey_jarvis', 'alexa']
        self.threshold = threshold
        self.is_running = False
        self.thread = None
        self.pyaudio_instance = None
        self.stream = None
        self.oww_model = None

    def start(self):
        """Menjalankan pendengar wake word di background thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        print("[WakeWord] Listener berhasil dimulai.")

    def stop(self):
        """Menghentikan pendengar wake word."""
        self.is_running = False
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

    def _listen_loop(self):
        CHUNK = 1280  # 80ms chunk pada sampel rate 16000 Hz
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        try:
            # Unduh model jika belum ada
            openwakeword.utils.download_models()
            
            # Inisialisasi model openWakeWord
            self.oww_model = Model(wakeword_models=self.target_models, inference_framework="onnx")
            
            self.pyaudio_instance = pyaudio.PyAudio()
            self.stream = self.pyaudio_instance.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )

            print(f"[WakeWord] Mendengarkan kata pemicu: {self.target_models}...")

            cooldown_seconds = 2.0  # Mencegah multiple trigger berturut-turut
            last_trigger_time = 0

            while self.is_running:
                try:
                    data = self.stream.read(CHUNK, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    
                    # Prediksi dengan openWakeWord
                    prediction = self.oww_model.predict(audio_data)

                    for model_name, score in self.oww_model.prediction_buffer.items():
                        current_score = score[-1]
                        if current_score >= self.threshold:
                            current_time = time.time()
                            if current_time - last_trigger_time > cooldown_seconds:
                                last_trigger_time = current_time
                                print(f"\n[WakeWord] DETEKSI! Kata: {model_name} (Skor: {current_score:.2f})")
                                if self.callback:
                                    self.callback(model_name)
                                break
                except Exception as e:
                    if self.is_running:
                        print(f"[WakeWord Loop Error] {e}")
                    time.sleep(0.1)

        except Exception as e:
            print(f"[WakeWord Initialization Error] {e}")
        finally:
            self.stop()

if __name__ == "__main__":
    def on_detected(model_name):
        print(f"🎉 WAKE WORD TERPAGIL! [{model_name}]")

    listener = WakeWordListener(callback=on_detected)
    listener.start()
    
    print("Tekan Ctrl+C untuk keluar...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        listener.stop()
