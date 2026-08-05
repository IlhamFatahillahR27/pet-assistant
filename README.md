# 🐈 Pet Assistant

**Pet Assistant** adalah aplikasi asisten virtual berbasis Python dengan antarmuka grafis (GUI Tkinter) berbentuk *floating widget* animasi kucing. Aplikasi ini terintegrasi langsung dengan **Google Gemini AI API**, dilengkapi kemampuan kata pemicu suara (*Wake Word Detection*), pengenalan suara (*Speech-To-Text*), pembacaan teks (*Text-To-Speech*), dan **Panel Pengaturan Terpisah**.

---

## ✨ Fitur Utama

- 🐱 **Floating Pet Widget**: Tampilan kucing animasi melayang tanpa bingkai (*frameless*) di atas layar komputer.
- ⚙️ **Panel Pengaturan Terpisah (Dedicated Settings Panel)**:
  - Akses melalui tombol ikon `⚙️` di header aplikasi.
  - Tampilan terpisah yang rapi untuk mengelola pengaturan tanpa mengganggu layar obrolan utama.
  - Struktur modular yang siap menampung pengaturan baru di masa mendatang.
- 🔊 **Toggle Membacakan Respon AI (TTS)**:
  - Sakelar ON/OFF untuk menentukan apakah asisten membacakan balasan berupa suara atau hanya teks.
  - Slider pengatur kecepatan suara (*TTS Speech Rate Slider*).
- 👂 **Wake on Command (Wake Word Detection)**:
  - Menggunakan engine **openWakeWord** (100% **Free & Open Source**).
  - Kata pemicu bawaan: **"Hey Jarvis"** dan **"Alexa"**.
  - Perekaman suara langsung terpicu otomatis tanpa perlu klik tombol.
  - **State Tombol Otomatis**: Tombol mikrofon akan otomatis berubah warna menjadi hijau aktif (`🎙️ Terpemicu (hey_jarvis)!`) saat kata pemicu terdeteksi dan kembali normal saat selesai.
  - Opsi toggle `👂 Wake Word` tersedia langsung di Panel Pengaturan.
- 🧠 **Gemini AI Brain**: Jawaban cerdas dan konteks percakapan yang berkelanjutan menggunakan Google Gemini SDK.
- 🎙️ **Speech-to-Text (STT) Bebas Pemotongan**:
  - Perekaman suara melalui Google Speech Recognition.
  - **Dioptimalkan untuk Penjelasan Panjang**: Batas jeda nafas (`pause_threshold`) ditingkatkan menjadi 2,0 detik dan durasi frasa hingga 30 detik agar percakapan tidak mendadak terputus saat Anda menjelaskan.

---

## 📁 Struktur Proyek

```text
pet-assisten/
├── robot_app.py           # Aplikasi utama GUI (Tkinter), manajemen view & state UI
├── wake_word_listener.py  # Modul pendeteksi Wake Word (openWakeWord background listener)
├── gemini_brain.py        # Modul integrasi AI Google Gemini API & sesi percakapan
├── stt.py                 # Modul Speech-To-Text (rekam suara -> teks)
├── tts.py                 # Modul Text-To-Speech (teks -> suara)
├── orange-cat.gif         # Aset animasi GIF kucing
├── .env.example           # Template konfigurasi environment variable
├── README.md              # Dokumentasi penggunaan aplikasi
└── requirements.txt       # Daftar dependensi modul Python
```

---

## 🛠️ Prasyarat & Instalasi

### 1. Prasyarat Sistem
- **Python 3.8 - 3.11**
- Mikrofon aktif untuk input suara (*Speech-to-Text* & *Wake Word*).
- Koneksi Internet untuk mengakses API Google Gemini dan Google STT.

### 2. Cara Instalasi

1. **Clone Repositori:**
   ```bash
   git clone https://github.com/username/pet-assisten.git
   cd pet-assisten
   ```

2. **Buat & Aktifkan Virtual Environment:**
   ```bash
   # Windows
   python -m venv env_asisten
   env_asisten\Scripts\activate
   ```

3. **Install Dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfigurasi Environment Variable (`.env`):**
   Salin file `.env.example` menjadi `.env`:
   ```bash
   copy .env.example .env
   ```
   Isi file `.env` dengan API Key dari Google AI Studio:
   ```env
   GOOGLE_AI_STUDIO_API_KEY=your_gemini_api_key_here
   AI_MODEL_KEY=gemini-1.5-flash
   ```

---

## 🚀 Cara Menjalankan Aplikasi

Jalankan skrip utama `robot_app.py`:

```bash
python robot_app.py
```

### 💡 Panduan Fitur Pengaturan & Suara:

1. **Buka Panel Pengaturan**:
   - Klik tombol **`⚙️`** di header bagian kanan atas.
   - Di sini Anda dapat:
     - Mengaktifkan/mematikan pembacaan suara AI (**`🔊 Membacakan Respon AI (TTS)`**).
     - Mengaktifkan/mematikan kata pemicu (**`👂 Wake Word`**).
     - Mengatur kecepatan bicara (**`🎚️ Kecepatan Suara`**).
   - Klik **`🔙 Kembali ke Chat`** (atau klik ikon `💬`) untuk kembali ke layar percakapan.

2. **Menggunakan Wake Word**:
   - Pastikan Wake Word aktif. Ucapkan **"Hey Jarvis"** atau **"Alexa"**.
   - Tombol mikrofon akan otomatis menyala hijau `🎙️ Terpemicu!` dan langsung merekam perintah Anda.

3. **Perekaman Manual & Input Teks**:
   - Klik **`🎤 Tanya Asisten`** atau ketik teks pada kolom chat lalu tekan `Enter`.

---

## ℹ️ Lisensi & Biaya Engine Wake Word

- Engine **openWakeWord** yang digunakan pada aplikasi ini **100% Free & Open Source (Apache License 2.0)** tanpa perlu pendaftaran, API key, atau biaya berlangganan.

---

## 📜 Lisensi Proyek

Proyek ini dibuat untuk tujuan edukasi dan pengembangan asisten personal.
