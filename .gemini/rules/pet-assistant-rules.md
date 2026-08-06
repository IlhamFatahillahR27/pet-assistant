# 🐈 Pet Assistant Project Instructions & System Rules

Setiap kali sesi obrolan baru dimulai di project `pet-assistant`, selalu terapkan aturan dan panduan berikut:

## 📁 Struktur Monorepo Architecture
- **Backend**: `backend/` (FastAPI REST API & WebSocket Server di `http://127.0.0.1:8000`).
  - `main.py`: Entry point server FastAPI.
  - `gemini_brain.py`: Integrasi Gemini AI dengan System Instruction Karakter Anime Manusia Kucing ('Kitty').
  - `stt.py`: Perekam suara Speech-To-Text (Google Recognition).
  - `tts.py`: Pembaca suara Text-To-Speech (pyttsx3 / Windows SAPI5).
  - `wake_word_listener.py`: Standby wake word listener cat-themed ("Hi Kitty", "Mew Mew", "Hey Kitty").
  - `settings_manager.py`: Manajemen `settings.json`.
  - `ws_manager.py`: WebSocket connection & broadcast manager.
- **Frontend**: `src/` (React + Vite + CSS Glassmorphism).
- **Tauri v2 Shell**: `src-tauri/` (Desktop frameless, transparent, always-on-top window).

## 🚀 Cara Menjalankan Aplikasi
- **Terminal 1 (Backend)**: `python backend/main.py`
- **Terminal 2 (Desktop App)**: `npm run tauri dev`
- **Verifikasi Build**: `npm run build`

## 🐱 Aturan Kepribadian & Tata Bahasa AI ('Kitty')
1. **Karakter Anime Manusia Kucing ('Kitty')**: Karakter ramah, hangat, pintar, dan menyenangkan (dapat menyisipkan bumbu khas kucing seperti "Nyaa~" atau "Meow~" secara proporsional).
2. **DILARANG KERAS Menggunakan Header Markdown**: Jangan pernah menggunakan simbol judul/heading berformat Markdown (`#`, `##`, `###`, `####`).
3. **Langsung To-The-Point (Direct Response)**:
   - Jika pengguna meminta lelucon, berikan HANYA 1 lelucon singkat langsung tanpa kata pengantar berlebihan.
   - Jika pengguna meminta penjelasan/informasi, jelaskan secara langsung dalam paragraf alami layaknya mentor/sahabat yang berbicara santai ke muridnya.
4. **Speech-Synced Text**: Teks balasan AI di layar obrolan ditampilkan secara *word-by-word streaming* (~90ms per kata) mengikuti irama pembacaan suara TTS.

## 🎙️ Aturan Keamanan Mikrofon & PortAudio (Windows)
1. **Auto-Pause Wake Word**: Saat STT atau perintah suara aktif, hentikan sementara background Wake Word listener (`wake_word_listener.stop_global_wake_word_listener()`).
2. **Hardware Release Delay**: Selalu berikan jeda `time.sleep(0.4-0.5)` setelah menghentikan listener agar driver PortAudio Windows membebaskan handle mikrofon secara bersih sebelum STT dibuka.
3. **Filter Threading Excepthook**: Gunakan `threading.excepthook` filter untuk meredam traceback PortAudio internal `OSError: [Errno -9988 / -9999] Stream closed` agar terminal tetap 100% bersih.

## 🪟 Windows WebView2 Native Dragging
- Gunakan `-webkit-app-region: drag` pada `.app-header` dan `.pet-widget-container` di `src/App.css`.
- Gunakan `-webkit-app-region: no-drag` pada tombol, input, dan elemen interaktif lainnya.
