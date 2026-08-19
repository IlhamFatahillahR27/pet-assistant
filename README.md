# 🐈 Pet Assistant (Desktop AI Floating Widget)

**Pet Assistant** adalah aplikasi asisten personal desktop interaktif berbentuk *floating widget* kucing animasi lucu tanpa bingkai (*frameless transparent window*) yang selalu melayang di atas layar (*always-on-top*). Dibangun menggunakan **Tauri v2 + React (Vite)** untuk antarmuka desktop yang ringan dan responsif, serta **Python FastAPI** sebagai backend cerdas multi-provider AI, pengenalan suara (*Speech-to-Text*), pendengar kata pemicu (*Cat Wake Word*), dan pembaca suara (*Text-to-Speech*).

---

## ✨ Fitur Utama

### 🤖 1. Multi-Model AI Brain Switcher
- **Multi-Provider Support**: Beralih bebas antara berbagai penyedia AI kelas dunia tanpa perlu restart aplikasi:
  - **Google Gemini**: Gemini 2.5 Flash, Gemini 2.5 Pro, Gemini 2.0 Flash.
  - **Groq Cloud (LPU)**: LLaMA 3.3 70B, LLaMA 3.1 8B, DeepSeek R1 Distill *(Inferensi ultra cepat)*.
  - **OpenAI**: GPT-4o Mini, GPT-4o, GPT-3.5 Turbo.
  - **DeepSeek**: DeepSeek-V3 (Chat) & DeepSeek-R1 (Reasoning).
  - **OpenRouter Cloud**: Gateway terpadu untuk ratusan model AI cloud.
  - **Ollama / LM Studio**: AI lokal 100% offline gratis tanpa internet.
  - **Custom Endpoint**: Kompatibel dengan API berspesifikasi OpenAI.
- **Live Connection Test**: Uji koneksi dan latensi model AI langsung dari panel pengaturan.
- **Konteks Percakapan & Streaming**: Respon teks muncul secara real-time via WebSocket.

### 🐱 2. Animasi Kucing Interaktif (Multi-Pose & Multi-Cat)
- **4 Pilihan Karakter Kucing**: Kucing Oranye (*Orange*), Kucing Hitam (*Black*), Kucing Belang (*Calico*), dan Kucing Putih (*White*).
- **Animasi Pose State Machine Real-time**:
  - `sit_forward`: Pose santai / idle menghadap depan.
  - `sit_backward`: Pose berpikir saat AI sedang memproses jawaban.
  - `licking`: Pose menjilat bulu saat asisten berbicara (TTS aktif).
  - `lifted`: Pose terangkat saat jendela di-drag / dipindahkan posisinya di desktop.
  - `sleeping`: Pose tidur otomatis saat pengguna AFK / tidak ada aktivitas selama 45 detik.
  - `hide_n_seek`: Animasi cilukba saat widget diklik cepat untuk minimize.

### 🧠 3. Memori & Habit Tracker Pengguna
- **Ekstraksi Memori Otomatis**: Asisten mengingat nama, hobi, makanan kesukaan, dan kebiasaan pengguna dari percakapan.
- **Injeksi Memori Cerdas**: Memori pengguna disisipkan ke context prompt AI untuk jawaban yang sangat personal.
- **Tab Manajemen Memori**: Lihat daftar memori yang tersimpan, hapus memori tertentu, atau reset seluruh memori.

### 🎙️ 4. Cat-Themed Wake Word & Speech Recognition
- **Kata Pemicu Kucing**: Panggil asisten dengan suara: **"Hi Kitty"**, **"Hey Kitty"**, **"Halo Kitty"**, **"Mew Mew"**, atau **"Kitty"**.
- **Auto-Start & Seamless Lifecycle**: Wake Word otomatis aktif sejak awal aplikasi dibuka.
- **Speech-to-Text (STT)**: Pengenalan suara bahasa Indonesia & Inggris yang responsif.

### 🔊 5. Text-to-Speech (TTS) WAV Audio Pipeline
- **Sintesis WAV & Pembersihan Otomatis**: Respon AI disintesis secara instan ke file audio WAV sementara dan diputar via Windows native WinMM API, lalu dihapus otomatis (`os.remove`) setelah selesai.
- **Eksekusi Asinkron (Concurrent)**: Teks jawaban muncul instan di UI bersamaan dengan pemutaran suara.
- **Dukungan Suara Sistem**: Mendukung suara bawaan Windows SAPI5 & OneCore Voices dengan slider kecepatan (*Speech Rate*) dan volume.

### 🎨 6. Tema Glassmorphism & Kontrol Desktop
- **4 Tema Estetik**: Mocha Dark, Sakura Pink, Mint Cyberpunk, dan Solar Amber.
- **Pencegahan Maximize Bug**: Jendela terkunci pada rasio widget dan tidak akan membesar/memenuhi layar saat di-klik ganda.
- **🔴 Tombol Shut Down / Tutup Aplikasi**: Tombol Power di bar navigasi untuk menutup jendela desktop dan menghentikan backend server secara bersih.

---

## 📁 Struktur Monorepo Proyek

```text
pet-assisten/
├── backend/                      # Python FastAPI Backend Server & AI Modules
│   ├── main.py                   # REST API, WebSocket Server & Shutdown Handler
│   ├── ai_brain.py               # Unified Multi-Provider AI Engine (Gemini, Groq, OpenAI, Ollama, dll.)
│   ├── gemini_brain.py           # Backward-compatibility layer
│   ├── wake_word_listener.py     # Thread-safe Cat Wake Word Listener
│   ├── stt.py                    # Speech-To-Text & Voice Command Processor
│   ├── tts.py                    # Text-To-Speech WAV Synthesis & WinSound Player
│   ├── user_memory_manager.py    # Persistent User Memory Manager (JSON)
│   ├── settings_manager.py       # Configuration & Settings Manager
│   ├── ws_manager.py             # Thread-safe WebSocket Broadcast Manager
│   ├── settings.json             # File penyimpanan konfigurasi lokal
│   └── user_memory.json          # File penyimpanan data memori pengguna
├── src/                          # React Frontend Source Code (Vite)
│   ├── assets/cats/              # Frame Sprite / GIF Karakter Kucing
│   ├── components/
│   │   ├── PetWidget.jsx         # Floating Cat Avatar Widget Component
│   │   ├── FrameAnimator.jsx     # Pose Frame Animation Engine
│   │   ├── ChatPanel.jsx         # Chat Messages, Input & Mic Controls
│   │   ├── MemoryPanel.jsx       # Tab Manajemen Memori Pengguna
│   │   ├── SettingsPanel.jsx     # Panel Pengaturan AI, Suara, Kucing & Tema
│   │   └── Header.jsx            # Bilah Navigasi, Drag Region & Tombol Shutdown
│   ├── services/
│   │   ├── websocket.js          # WebSocket Client Service
│   │   └── api.js                # FastAPI REST API Client
│   ├── App.jsx                   # Root Application State & Event Coordinator
│   ├── App.css                   # Glassmorphism Styling & Responsive Theme Engine
│   └── main.jsx                  # React Entry Point
├── src-tauri/                    # Tauri v2 Desktop Engine & Rust Configuration
│   ├── src/
│   │   ├── main.rs               # Rust Binary Entry Point
│   │   └── lib.rs                # Window Event Coordinator (Moving, Close/Exit)
│   ├── capabilities/
│   │   └── default.json          # Desktop Window & Process Permissions
│   ├── tauri.conf.json           # Frameless, Transparent, Locked Maximize Config
│   └── Cargo.toml                # Rust Dependencies
├── package.json                  # React + Vite + Tauri Dependencies
├── vite.config.js                # Vite Bundler Config
├── requirements.txt              # Python Backend Dependencies
├── README.md                     # Dokumentasi Proyek
└── ROADMAP.md                    # Roadmap & Status Pengembangan
```

---

## 🛠️ Prasyarat & Panduan Instalasi

### 1. Prasyarat Sistem
- **Node.js (v18+)** & **npm**
- **Python 3.10 - 3.12**
- **Rust & Cargo** (untuk build aplikasi desktop via Tauri v2)
- Mikrofon & Speaker aktif.

### 2. Langkah Instalasi

```bash
# 1. Clone repositori
git clone https://github.com/IlhamFatahillahR27/pet-assistant.git
cd pet-assisten

# 2. Setup Virtual Environment Python
python -m venv env_asisten
env_asisten\Scripts\activate

# 3. Install dependensi Python backend
pip install -r requirements.txt

# 4. Install dependensi Frontend React & Tauri
npm install
```

---

## 🔑 Link Portal Resmi Mendapatkan API Key AI

Aplikasi mendukung input API Key langsung melalui **Menu Pengaturan (⚙️) -> Tab Model AI** di dalam aplikasi, tersimpan aman dan privat di komputer lokal Anda:

| Penyedia AI | Model Utama / Keunggulan | Link Portal API Key Resmi |
| :--- | :--- | :--- |
| **Google Gemini** | Gemini 2.5 Flash / Pro, Gemini 2.0 *(Konteks Panjang & Cerdas)* | 🔗 [Google AI Studio API Keys](https://aistudio.google.com/app/apikey) |
| **Groq Cloud** | LLaMA 3.3 70B, LLaMA 3.1 8B, DeepSeek R1 *(LPU Kecepatan Tinggi)* | 🔗 [Groq Cloud Console Keys](https://console.groq.com/keys) |
| **OpenAI** | GPT-4o Mini, GPT-4o, GPT-3.5 Turbo *(Standar ChatGPT)* | 🔗 [OpenAI Platform API Keys](https://platform.openai.com/api-keys) |
| **DeepSeek** | DeepSeek-V3 (Chat) & DeepSeek-R1 (Reasoning) *(Efisien)* | 🔗 [DeepSeek Platform API Keys](https://platform.deepseek.com/api_keys) |
| **OpenRouter** | Akses ke ratusan model AI cloud dalam 1 API Key | 🔗 [OpenRouter Keys Portal](https://openrouter.ai/keys) |
| **Ollama** | Model Lokal Offline (LLaMA 3, Mistral, Qwen 2.5) *(Gratis)* | 🔗 [Ollama Official Website](https://ollama.com) |
| **LM Studio** | Local LLM Server dengan antarmuka desktop | 🔗 [LM Studio Download](https://lmstudio.ai) |

---

## 🚀 Cara Menjalankan Aplikasi

Jalankan backend server dan desktop app dalam dua terminal terpisah:

### Terminal 1: Backend Python
```bash
# Aktifkan virtual environment
env_asisten\Scripts\activate

# Jalankan server FastAPI
python backend/main.py
```
*Server FastAPI berjalan di `http://127.0.0.1:8000` dan WebSocket di `ws://127.0.0.1:8000/ws`.*

### Terminal 2: Desktop Frontend (Tauri v2)
```bash
# Jalankan aplikasi Desktop Floating Widget
npm run tauri dev
```
*(Atau gunakan `npm run dev` jika ingin menjalankan mode preview di browser web).*

---

## 💡 Panduan Penggunaan Fitur

1. **Memanggil dengan Suara (*Wake Word*)**:
   - Ucapkan *"Hi Kitty"* atau *"Hey Kitty"*.
   - Tombol mikrofon akan menyala dan asisten akan langsung mendengarkan perintah Anda.
2. **Menggeser Posisi Kucing (*Drag & Drop*)**:
   - Klik dan tahan badan kucing untuk memindahkannya ke posisi mana pun di desktop.
3. **Membuka Panel Pengaturan**:
   - Klik ikon `⚙️` di header untuk mengganti model AI, memilih karakter kucing, mengubah tema warna, atau mengatur suara.
4. **Melihat & Mengelola Memori**:
   - Klik ikon `🧠` di header untuk melihat hal-hal yang diingat asisten tentang Anda.
5. **Menutup / Mematikan Aplikasi**:
   - Klik ikon daya merah `⏻` di pojok kanan atas header untuk keluar dari aplikasi dan menghentikan backend secara otomatis.

---

## 📜 Lisensi
Proyek ini dibuat untuk tujuan edukasi, eksplorasi AI agentik, dan pengembangan asisten personal desktop modern.
