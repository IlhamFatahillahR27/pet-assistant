import os
import json
import threading

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

DEFAULT_SETTINGS = {
    "ai_model": os.getenv("AI_MODEL_KEY", "gemini-1.5-flash"),
    "language": "id-ID",
    "tts": {
        "enabled": True,
        "rate": 160,
        "volume": 1.0,
        "language": "id"
    },
    "wake_word": {
        "enabled": True,
        "target_models": ["hey_jarvis", "alexa"],
        "threshold": 0.5
    }
}


class SettingsManager:
    def __init__(self, file_path=SETTINGS_FILE):
        self.file_path = file_path
        self._lock = threading.Lock()
        self._settings = self.load_settings()

    def load_settings(self) -> dict:
        """Memuat settings dari file JSON atau membuat default jika belum ada."""
        with self._lock:
            if not os.path.exists(self.file_path):
                self._save_file(DEFAULT_SETTINGS)
                return DEFAULT_SETTINGS.copy()
            
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Gabungkan dengan default untuk mencegah missing keys
                    merged = DEFAULT_SETTINGS.copy()
                    merged.update(data)
                    return merged
            except Exception as e:
                print(f"[SettingsManager Error] Gagal membaca settings.json: {e}")
                return DEFAULT_SETTINGS.copy()

    def get_settings(self) -> dict:
        """Mengembalikan dictionary settings saat ini."""
        with self._lock:
            return self._settings.copy()

    def update_settings(self, new_data: dict) -> dict:
        """Memperbarui settings dan menyimpannya ke file JSON."""
        with self._lock:
            def deep_update(d, u):
                for k, v in u.items():
                    if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                        deep_update(d[k], v)
                    else:
                        d[k] = v

            deep_update(self._settings, new_data)
            self._save_file(self._settings)
            return self._settings.copy()

    def _save_file(self, data: dict):
        """Menyimpan dictionary ke file JSON."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[SettingsManager Error] Gagal menyimpan settings.json: {e}")

# Singleton instance
settings_manager = SettingsManager()
