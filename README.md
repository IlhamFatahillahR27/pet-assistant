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
- **🔴 Tombol Shut Down / Tutup Aplikasi**: Tombol Power di bar navigasi untuk menutup jendela desktop dan menghentikan backend secara bersih.

### 🌐 7. Integrasi Google OAuth & Google Workspace (Fase 8)
- **Google OAuth 2.0 Desktop Login**: Hubungkan akun Google secara aman melalui browser bawaan dengan alur redirect lokal dan auto-refresh token.
- **📅 Google Calendar**: Kitty dapat melihat jadwal agenda mendatang dan mencatat kegiatan baru ke kalender Google Anda.
- **✅ Google Tasks**: Kitty dapat membaca to-do list aktif, menambah tugas baru, dan menandai tugas selesai lewat perintah suara/chat.
- **✉️ Gmail Assistant**: Kitty dapat membaca cuplikan email masuk yang belum dibaca (*unread inbox*) dan mengirim email langsung.
- **Google Hub UI**: Tab interaktif di Settings untuk memantau kalender, checklist tugas to-do, dan cuplikan email secara visual.

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

# 5. Salin file template konfigurasi .env (Opsional jika ingin mengatur API Key lewat file)
copy .env.example .env

# 6. Salin file template settings default (Opsional, backend juga dapat membuatnya otomatis)
copy backend\settings.example.json backend\settings.json
```

### ⚙️ 3. Panduan Penggunaan File Template (`.example`)

Untuk menjaga keamanan token dan kredensial API agar tidak bocor ke publik, repositori ini menyertakan file template berekstensi `.example`:

| File Template | File Target di Komputer Lokal | Cara Penggunaan & Tujuan |
| :--- | :--- | :--- |
| **`.env.example`** | **`.env`** *(Root Project)* | Salin (`copy .env.example .env`) lalu isi nilai API Key (Gemini, Groq, dll.) serta `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET`. |
| **`backend/settings.example.json`** | **`backend/settings.json`** | Salin (`copy backend\settings.example.json backend\settings.json`) untuk inisialisasi pengaturan awal (karakter kucing, volume TTS, provider AI default). Jika dilewati, backend akan otomatis membuatnya saat pertama kali dijalankan. |
| **`backend/user_memory.example.json`** | **`backend/user_memory.json`** | *Referensi Skema*: File format memori pengguna. File `user_memory.json` akan dibuat dan dikelola otomatis oleh backend saat Kitty mengingat fakta baru dari obrolan. |
| **`backend/google_tokens.example.json`** | **`backend/google_tokens.json`** | *Referensi Skema*: File format token OAuth Google. File `google_tokens.json` akan dibuat otomatis saat Anda pertama kali login via browser. |

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

## 🔐 Panduan Setup Google OAuth 2.0 (Client ID & Secret)

Untuk mengaktifkan fitur **Google Workspace (Google Calendar, Tasks, Gmail)** di Pet Assistant, Anda memerlukan **Google OAuth Client ID & Secret** dari Google Cloud Console *(100% Gratis & Tanpa Perlu Kartu Kredit)*:

### 🛠️ Langkah Pembuatan Kredensial di Google Cloud Console:

1. **Buka Google Cloud Console**:
   - Kunjungi [console.cloud.google.com](https://console.cloud.google.com/).
   - Buat Project Baru (misal: `Pet Assistant Desktop`) atau pilih project yang sudah ada.

2. **Aktifkan 3 APIs Google Workspace**:
   - Di menu navigasi samping, buka **APIs & Services > Library** (atau gunakan kotak pencarian atas).
   - Cari dan klik tombol **Enable** (Aktifkan) untuk masing-masing 3 API berikut:
     - 📅 **Google Calendar API**
     - ✅ **Google Tasks API**
     - ✉️ **Gmail API**

3. **Konfigurasi OAuth Consent Screen**:
   - Buka menu **APIs & Services > OAuth consent screen**.
   - Pilih User Type: **External** -> Klik **Create**.
   - Isi form data dasar:
     - **App name**: `Pet Assistant`
     - **User support email**: (Pilih email Anda)
     - **Developer contact information**: (Ketik email Anda)
   - Klik **Save and Continue** sampai ke langkah **Test users**.
   - ⚠️ **PENTING (Test users)**: Klik tombol **+ ADD USERS**, lalu masukkan email Google Anda sendiri. *(Langkah ini wajib agar akun Anda dapat langsung login tanpa perlu verifikasi publik Google)*.
   - Klik **Save and Continue** hingga selesai.

4. **Buat Kredensial OAuth Client ID**:
   - Buka menu **APIs & Services > Credentials**.
   - Klik **+ CREATE CREDENTIALS** -> Pilih **OAuth client ID**.
   - **Application type**: Pilih **Web application**.
   - **Name**: `Pet Assistant Client`.
   - Di bagian **Authorized redirect URIs**, klik tombol **+ ADD URI**, lalu masukkan persis URI callback lokal berikut:
     ```text
     http://127.0.0.1:8000/api/google/oauth/callback
     ```
   - Klik **CREATE**.
   - Jendela pop-up akan muncul menampilkan **Your Client ID** dan **Your Client Secret**. Salin kedua nilai tersebut.

5. **Simpan Kredensial ke Pet Assistant**:
   - **Cara 1 (Langsung dari UI Aplikasi)**:
     - Buka Pet Assistant -> Klik ikon `⚙️` (Pengaturan) -> Pilih Tab **"Google Hub"**.
     - Buka menu **"Kredensial OAuth Google Cloud (Opsional)"**.
     - Masukkan **Client ID** dan **Client Secret** Anda, lalu klik **"Simpan Kredensial Google"**.
   - **Cara 2 (Melalui file `.env` di root project)**:
     ```env
     GOOGLE_CLIENT_ID=isi_client_id_anda.apps.googleusercontent.com
     GOOGLE_CLIENT_SECRET=GOCSPX-isi_client_secret_anda
     ```
   - Setelah disimpan, klik tombol **"🔗 Login & Hubungkan Akun Google"** di aplikasi. Jendela browser akan terbuka meminta izin, dan akun Anda akan langsung terhubung secara otomatis ke Kitty! 🎉

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
