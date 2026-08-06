# 🐈 Pet Assistant

**Pet Assistant** adalah aplikasi asisten virtual berbasis **Tauri v2 + React (Vite)** dan **Backend Python FastAPI** berbentuk *floating widget* animasi kucing melayang di desktop. Aplikasi ini terintegrasi dengan **Google Gemini AI API**, dilengkapi kata pemicu suara (*Wake Word Detection* bertema kucing: **"Hi Kitty"**, **"Mew Mew"**, **"Hey Kitty"**), pengenalan suara (*Speech-To-Text*), pembacaan teks (*Text-To-Speech*), dan **Panel Pengaturan Terpisah (Glassmorphism Dark Theme)**.

---

## ✨ Fitur Utama

- 🐱 **Floating Pet Widget (Tauri v2 + React)**: Tampilan kucing animasi melayang tanpa bingkai (*frameless*), background transparan (*transparent*), dan selalu di atas (*always-on-top*).
- ⚙️ **Panel Pengaturan Terpisah (Dedicated Settings Panel)**:
  - Akses melalui tombol ikon `⚙️` di header aplikasi React.
  - Pengelolaan pengaturan terpisah dengan gaya *Dark Glassmorphic UI*.
- 🔊 **Toggle Membacakan Respon AI (TTS)**:
  - Sakelar ON/OFF untuk menentukan apakah asisten membacakan balasan berupa suara atau hanya teks.
  - Slider pengatur kecepatan suara (*TTS Speech Rate Slider*).
- 👂 **Wake on Command (Cat-Themed Wake Word)**:
  - Kata pemicu bertema kucing: **"Hi Kitty"**, **"Mew Mew"**, dan **"Hey Kitty"**.
  - **Hybrid Keyword Spotter + openWakeWord Engine**: Perekaman suara terpemicu otomatis saat ucapan terdeteksi.
  - **State Tombol Otomatis**: Tombol mikrofon menyala hijau aktif (`🎙️ Terpemicu!`) saat kata pemicu terdeteksi.
- 🧠 **Gemini AI Brain**: Jawaban cerdas dan konteks percakapan berkelanjutan menggunakan Google Gemini SDK.
- ⚡ **Real-Time WebSocket Sync**: Komunikasi *real-time* antara Frontend React dan Backend Python via WebSocket (`ws://127.0.0.1:8000/ws`).

---

## 📁 Struktur Proyek (Monorepo Layout)

```text
pet-assisten/
├── backend/                      # Python FastAPI Backend Server & Modules
│   ├── main.py                   # REST API & WebSocket Server
│   ├── wake_word_listener.py     # Hybrid Cat Wake Word Listener
│   ├── gemini_brain.py           # Google Gemini AI Integration
│   ├── stt.py                    # Speech-To-Text Module
│   ├── tts.py                    # Text-To-Speech Module
│   ├── settings_manager.py       # Configuration Manager
│   ├── ws_manager.py             # WebSocket Client Connection Manager
│   └── settings.json             # Settings configuration file
├── src/                          # React Frontend Source Code (Vite)
│   ├── assets/
│   │   └── orange-cat.gif        # Animasi Widget Kucing
│   ├── components/
│   │   ├── PetWidget.jsx         # Floating Cat Avatar Widget Component
│   │   ├── ChatPanel.jsx         # Chat Messages & Input Panel
│   │   ├── SettingsPanel.jsx     # Dedicated Settings View Panel
│   │   └── Header.jsx            # Header & Control Action Buttons
│   ├── services/
│   │   ├── websocket.js          # WebSocket Client Service
│   │   └── api.js                # FastAPI REST API Service
│   ├── App.jsx                   # React Entry Component & State Manager
│   ├── App.css                   # Glassmorphism Dark Theme Styling
│   └── main.jsx                  # React Entry Point
├── src-tauri/                    # Tauri v2 Desktop Shell & Config
│   ├── src/
│   │   ├── main.rs               # Rust Entry Point
│   │   └── lib.rs                # Tauri App Runner
│   ├── tauri.conf.json           # Frameless, Transparent & Always-on-Top Config
│   └── Cargo.toml                # Rust Dependencies
├── package.json                  # React + Vite + Tauri Dependencies
├── vite.config.js                # Vite Bundler Config
├── requirements.txt              # Python Backend Dependencies
├── README.md                     # Documentation
└── ROADMAP.md                    # Project Roadmap
```

---

## 🛠️ Prasyarat & Instalasi

### 1. Prasyarat Sistem
- **Node.js (v18+)** & **npm**
- **Python 3.8 - 3.11**
- **Rust / Cargo** (untuk build desktop app via Tauri v2)
- Mikrofon aktif untuk input suara (*Speech-to-Text* & *Wake Word*).

### 2. Cara Instalasi

1. **Clone Repositori:**
   ```bash
   git clone https://github.com/username/pet-assisten.git
   cd pet-assisten
   ```

2. **Install Dependensi Python & Frontend:**
   ```bash
   # Virtual environment Python
   python -m venv env_asisten
   env_asisten\Scripts\activate

   # Install dependensi Python backend
   pip install -r requirements.txt

   # Install dependensi Node.js / React frontend
   npm install
   ```

3. **Konfigurasi Environment Variable (`backend/.env`):**
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

---

## 🚀 Cara Menjalankan Aplikasi

### Langkah 1: Menjalankan Backend Python Server (Wajib)

Jalankan FastAPI & WebSocket Server terlebih dahulu:

```bash
# Aktifkan virtual environment
env_asisten\Scripts\activate

# Menjalankan backend server
python backend/main.py
```
*Server backend berjalan di `http://127.0.0.1:8000` (WebSocket di `ws://127.0.0.1:8000/ws`).*

---

### Langkah 2: Menjalankan Application Frontend / Desktop App

Buka terminal baru di direktori `pet-assisten/`:

#### Option A: Menjalankan Mode Desktop App (Tauri v2 Floating Window)
```bash
npm run tauri dev
```

#### Option B: Menjalankan Mode Browser Preview (React Vite)
```bash
npm run dev
```

---

## 💡 Panduan Fitur Pengaturan & Suara

1. **Menggunakan Wake Word Kucing**:
   - Ucapkan salah satu kata pemicu: **"Hi Kitty"**, **"Mew Mew"**, atau **"Hey Kitty"**.
   - Widget akan otomatis mendeteksi suara dan mengaktifkan perekaman jawaban.

2. **Membuka Panel Pengaturan**:
   - Klik ikon **`⚙️`** di header bagian kanan atas.
   - Atur sakelar **TTS**, **Wake Word**, atau **Kecepatan Suara**.

---

## 🤖 Antigravity AI Rules & Sesi Obrolan Baru

Proyek ini telah dilengkapi dengan aturan proyek terpusat (*project custom rules*) di [.gemini/rules/pet-assistant-rules.md](file:///D:/pribadi/Projects/pet-assisten/.gemini/rules/pet-assistant-rules.md).

Setiap kali Anda membuka sesi obrolan baru di **Antigravity CLI / IDE**, sistem akan otomatis membaca aturan proyek ini yang mencakup:
- Arsitektur Monorepo (`backend/`, `src/`, `src-tauri/`).
- Karakter & Tata Bahasa Anime Manusia Kucing 'Kitty' (Ramah, tanpa Markdown header, direct response).
- Penanganan mikrofon & jeda pelepasan hardware audio PortAudio Windows.
- Aturan WebView2 Native Dragging (`-webkit-app-region: drag`).

---

## 📜 Lisensi Proyek

Proyek ini dibuat untuk tujuan edukasi dan pengembangan asisten personal desktop modern.
