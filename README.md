# 🐈 Pet Assistant

**Pet Assistant** adalah aplikasi asisten virtual berbasis Python dengan antarmuka grafis (GUI Tkinter) berbentuk *floating widget* animasi kucing. Aplikasi ini terintegrasi langsung dengan **Google Gemini AI API**, dilengkapi kemampuan pengenalan suara (*Speech-To-Text*) dan pembacaan teks (*Text-To-Speech*).

---

## ✨ Fitur Utama

- 🐱 **Floating Pet Widget**: Tampilan kucing animasi melayang tanpa bingkai (*frameless*) di atas layar komputer.
- 🧠 **Gemini AI Brain**: Jawaban cerdas dan konteks percakapan yang berkelanjutan menggunakan Google Gemini SDK.
- 🎙️ **Speech-to-Text (STT)**: Berbicara langsung ke asisten menggunakan mikrofon melalui integrasi Google Speech Recognition.
- 💬 **Panel Chat Modern**:
  - Tema gelap (*Catppuccin Mocha inspired*).
  - Fitur Sembunyikan/Tampilkan (*Expand & Collapse*).
  - Penyesuaian ukuran window (*Resizable* dari sisi atas dan kiri).
  - Tombol **Reset Chat** untuk memulai topik percakapan baru.
- 🔊 **Text-to-Speech (TTS)**: Pembacaan jawaban teks ke dalam bentuk suara dengan dukungan Windows OneCore & SAPI5.

---

## 📁 Struktur Proyek

```text
pet-assisten/
├── robot_app.py        # Aplikasi utama GUI (Tkinter) & manajemen layout window
├── gemini_brain.py     # Modul integrasi AI Google Gemini API & sesi percakapan
├── stt.py              # Modul Speech-To-Text (rekam suara -> teks)
├── tts.py              # Modul Text-To-Speech (teks -> suara)
├── orange-cat.gif      # Aset animasi GIF kucing
├── .env.example        # Template konfigurasi environment variable
├── .gitignore          # Daftar file/folder yang diabaikan oleh Git
└── requirements.txt    # Daftar dependensi modul Python
```

---

## 🛠️ Prasyarat & Instalasi

### 1. Prasyarat Sistem
- **Python 3.8+**
- Mikrofon aktif untuk input suara (*Speech-to-Text*).
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

### Kontrol GUI & Penggunaan:
- **Tanya via Suara**: Klik tombol **🎤 Tanya Asisten** dan mulai berbicara.
- **Tanya via Teks**: Ketik pertanyaan di kolom input lalu tekan `Enter` atau tombol **✉️ Kirim**.
- **Geser Window**: Klik dan tahan karakter kucing untuk menggeser aplikasi di layar.
- **Toggle Chat**: Klik sekali pada karakter kucing untuk menyembunyikan/menampilkan panel chat.
- **Reset Chat**: Klik tombol **🔄 Reset** di pojok kanan atas chat untuk mengosongkan riwayat percakapan.
- **Keluar Aplikasi**: Tekan tombol `Esc` di keyboard.

---

## 📜 Lisensi

Proyek ini dibuat untuk tujuan edukasi dan pengembangan asisten personal.
