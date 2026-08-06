import os
import json
import time
import threading
from typing import List, Dict, Any, Optional

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "user_memory.json")

DEFAULT_MEMORY_STRUCTURE = {
    "memories": []
}

VALID_CATEGORIES = ["identity", "preference", "habit", "general"]


class UserMemoryManager:
    def __init__(self, file_path=MEMORY_FILE):
        self.file_path = file_path
        self._lock = threading.Lock()
        self._memories = self.load_memories()

    def load_memories(self) -> List[Dict[str, Any]]:
        """Memuat daftar memori dari file JSON atau menginisialisasi default jika file belum ada."""
        with self._lock:
            if not os.path.exists(self.file_path):
                self._save_file(DEFAULT_MEMORY_STRUCTURE)
                return []

            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("memories", [])
            except Exception as e:
                print(f"[UserMemoryManager Error] Gagal membaca user_memory.json: {e}")
                return []

    def get_all_memories(self) -> List[Dict[str, Any]]:
        """Mengembalikan salinan daftar memori pengguna saat ini."""
        with self._lock:
            return list(self._memories)

    def add_memory(self, fact: str, category: str = "general") -> Dict[str, Any]:
        """Menambahkan fakta baru tentang pengguna secara manual atau otomatis."""
        clean_fact = fact.strip()
        if not clean_fact:
            raise ValueError("Fakta tidak boleh kosong")

        cat = category.lower() if category.lower() in VALID_CATEGORIES else "general"

        with self._lock:
            # Cegah duplikasi fakta persis
            for item in self._memories:
                if item["fact"].lower() == clean_fact.lower():
                    return item

            new_item = {
                "id": f"mem_{int(time.time() * 1000)}",
                "fact": clean_fact,
                "category": cat,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
            self._memories.append(new_item)
            self._save_file({"memories": self._memories})
            return new_item

    def delete_memory(self, memory_id: str) -> bool:
        """Menghapus satu item memori berdasarkan ID."""
        with self._lock:
            initial_len = len(self._memories)
            self._memories = [m for m in self._memories if m.get("id") != memory_id]
            if len(self._memories) < initial_len:
                self._save_file({"memories": self._memories})
                return True
            return False

    def clear_all_memories(self) -> bool:
        """Menghapus seluruh daftar memori pengguna."""
        with self._lock:
            self._memories = []
            self._save_file({"memories": []})
            return True

    def get_memory_context_string(self) -> str:
        """
        Menyusun ringkasan fakta memori pengguna sebagai instruksi kontekstual
        untuk disisipkan ke system_instruction Gemini.
        """
        memories = self.get_all_memories()
        if not memories:
            return ""

        lines = ["\n\n--- DOKUMEN MEMORI & KETAHUAN LOKAL PENGGUNA ---"]
        lines.append("Berikut adalah fakta & kebiasaan yang kamu ingat tentang pengguna ini (Gunakan pengetahuan ini secara alami saat menjawab):")
        for idx, item in enumerate(memories, 1):
            cat_label = item.get("category", "general").upper()
            lines.append(f"{idx}. [{cat_label}] {item['fact']}")
        lines.append("--------------------------------------------------\n")
        return "\n".join(lines)

    def _save_file(self, data: dict):
        """Menyimpan data memori ke file user_memory.json."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[UserMemoryManager Error] Gagal menyimpan user_memory.json: {e}")

    def extract_facts_async(self, prompt_text: str, response_text: str, on_updated_callback=None):
        """
        Menjalankan ekstraksi fakta AI di background thread setelah percakapan selesai.
        Jika fakta baru ditemukan, disimpan ke file dan memanggil callback/ws broadcast.
        """
        def _bg_extract():
            try:
                import google.generativeai as genai
                # Jangan lakukan ekstraksi untuk prompt yang terlalu singkat
                if len(prompt_text.strip()) < 4:
                    return

                extraction_prompt = (
                    "Kamu adalah extractor memori otomatis.\n"
                    "Analisis pesan dari pengguna berikut:\n"
                    f"Pesan Pengguna: \"{prompt_text}\"\n\n"
                    "Apakah pesan pengguna tersebut secara eksplisit menyatakan fakta persisten baru tentang dirinya "
                    "(seperti nama panggilan, makanan/minuman favorit, hobi, profesi, atau jam rutinitas/kebiasaan)?\n\n"
                    "Aturan:\n"
                    "1. Jika TIDAK ada fakta baru tentang pengguna, balaskan HANYA kata 'NONE'.\n"
                    "2. Jika ADA fakta baru, balaskan HANYA JSON array berformat:\n"
                    '[{"fact": "fakta singkat tentang pengguna", "category": "identity|preference|habit|general"}]\n'
                    "Contoh kategori:\n"
                    "- identity: nama, profesi, tempat tinggal\n"
                    "- preference: makanan/minuman/hobi/warna kesukaan\n"
                    "- habit: jam tidur, jam bangun, rutinitas\n"
                    "- general: fakta umum pengguna\n"
                    "PENTING: Jangan sertakan Markdown codeblock fence (seperti ```json), kembalikan raw JSON saja."
                )

                model = genai.GenerativeModel("gemini-1.5-flash")
                resp = model.generate_content(extraction_prompt)
                raw_text = resp.text.strip() if resp and resp.text else "NONE"

                # Bersihkan dari markdown syntax jika ada
                if raw_text.startswith("```"):
                    lines = raw_text.splitlines()
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    raw_text = "\n".join(lines).strip()

                if raw_text.upper() != "NONE" and raw_text.startswith("["):
                    extracted_list = json.loads(raw_text)
                    added_any = False
                    for item in extracted_list:
                        fact_str = item.get("fact")
                        cat_str = item.get("category", "general")
                        if fact_str:
                            self.add_memory(fact_str, cat_str)
                            added_any = True
                            print(f"[Memory Auto-Extract] Fakta baru tersimpan: [{cat_str}] {fact_str}")

                    if added_any and on_updated_callback:
                        on_updated_callback(self.get_all_memories())
            except Exception as e:
                print(f"[Memory Auto-Extract Notice] Skip extraction: {e}")

        threading.Thread(target=_bg_extract, daemon=True).start()


# Singleton instance
user_memory_manager = UserMemoryManager()

