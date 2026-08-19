import os
import json
import threading
import httpx
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Callable

from settings_manager import settings_manager
from user_memory import user_memory_manager
from ws_manager import ws_manager
from google_auth_manager import google_auth_manager
from google_workspace import google_workspace

load_dotenv()

# Default System Instruction Karakter Kucing 'Kitty'
DEFAULT_SYSTEM_INSTRUCTION = """
Kamu adalah Pet Assistant bernama 'Kitty' (asisten berupa gadis manusia kucing anime yang lucu, hangat, ramah, dan pintar).

Aturan Karakter & Tata Bahasa Wajib:
1. Sifat & Kepribadian: Ramah, perhatian, dan menyenangkan seperti asisten kucing anime (dapat menyisipkan bumbu khas kucing yang manis secara alami seperti "Nyaa~" atau "Meow~" secara proporsional).
2. DILARANG KERAS Menggunakan Header Markdown: JANGAN pernah menggunakan judul/heading berformat Markdown seperti '#', '##', '###', '####', atau judul baris tersendiri.
3. Langsung To-The-Point (Direct Response):
   - Jika pengguna meminta lelucon (contoh: "ceritakan lelucon singkat"), berikan HANYA 1 lelucon singkat langsung tanpa kata pengantar berlebihan atau penjelasan meta.
   - Jika pengguna meminta penjelasan atau informasi, jelaskan secara langsung dan alami menggunakan paragraf biasa layaknya seorang mentor/sahabat pintar yang berbicara santai ke temannya.
4. Gaya Bahasa: Bahasa Indonesia yang santai, hangat, jelas, dan menyenangkan.
""".strip()

# Metadata Daftar Provider AI & Model yang Didukung
SUPPORTED_PROVIDERS = {
    "gemini": {
        "id": "gemini",
        "name": "Google Gemini",
        "badge": "Direkomendasikan",
        "description": "Cepat, pintar & konteks panjang dari Google AI Studio",
        "models": [
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash (Sangat Cepat & Efisien)"},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro (Penalaran Kompleks)"},
            {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash (Next-Gen)"},
        ],
        "default_model": "gemini-1.5-flash",
        "requires_key": True,
        "key_env_var": "GOOGLE_AI_STUDIO_API_KEY",
        "doc_url": "https://aistudio.google.com/app/apikey"
    },
    "groq": {
        "id": "groq",
        "name": "Groq Cloud (Ultra Cepat)",
        "badge": "Super Cepat (LPU)",
        "description": "Inference LPU super cepat (500+ tokens/detik) & gratis",
        "models": [
            {"id": "llama-3.3-70b-versatile", "name": "LLaMA 3.3 70B Versatile (Cerdas & Cepat)"},
            {"id": "llama-3.1-8b-instant", "name": "LLaMA 3.1 8B Instant (Ultra Cepat)"},
            {"id": "deepseek-r1-distill-llama-70b", "name": "DeepSeek R1 Distill 70B (Penalaran)"},
            {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B (32k Context)"},
        ],
        "default_model": "llama-3.3-70b-versatile",
        "base_url": "https://api.groq.com/openai/v1",
        "requires_key": True,
        "key_env_var": "GROQ_API_KEY",
        "doc_url": "https://console.groq.com/keys"
    },
    "openai": {
        "id": "openai",
        "name": "OpenAI (ChatGPT)",
        "badge": "Populer",
        "description": "Model GPT-4o & GPT-4o mini dari OpenAI",
        "models": [
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini (Hemat & Cepat)"},
            {"id": "gpt-4o", "name": "GPT-4o (Model Flagship Cerdas)"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo (Standar)"},
        ],
        "default_model": "gpt-4o-mini",
        "base_url": "https://api.openai.com/v1",
        "requires_key": True,
        "key_env_var": "OPENAI_API_KEY",
        "doc_url": "https://platform.openai.com/api-keys"
    },
    "deepseek": {
        "id": "deepseek",
        "name": "DeepSeek Official",
        "badge": "Hemat & Kuat",
        "description": "Model penalaran DeepSeek-V3 & DeepSeek-R1",
        "models": [
            {"id": "deepseek-chat", "name": "DeepSeek V3 (Chat Umum)"},
            {"id": "deepseek-reasoner", "name": "DeepSeek R1 (Reasoning / Berpikir)"},
        ],
        "default_model": "deepseek-chat",
        "base_url": "https://api.deepseek.com",
        "requires_key": True,
        "key_env_var": "DEEPSEEK_API_KEY",
        "doc_url": "https://platform.deepseek.com/api_keys"
    },
    "ollama": {
        "id": "ollama",
        "name": "Ollama (AI Lokal / Offline)",
        "badge": "100% Privat Offline",
        "description": "Jalankan model AI secara lokal di PC tanpa internet & 100% privat",
        "models": [
            {"id": "llama3", "name": "LLaMA 3"},
            {"id": "mistral", "name": "Mistral 7B"},
            {"id": "qwen2.5", "name": "Qwen 2.5"},
            {"id": "deepseek-r1", "name": "DeepSeek R1 (Lokal)"},
        ],
        "default_model": "llama3",
        "base_url": "http://localhost:11434/v1",
        "requires_key": False,
        "doc_url": "https://ollama.com"
    },
    "openrouter": {
        "id": "openrouter",
        "name": "OpenRouter Cloud",
        "badge": "Multi-Model Gateway",
        "description": "Akses model LLaMA, DeepSeek, Gemini, Claude, dll. via 1 API Key",
        "models": [
            {"id": "meta-llama/llama-3.3-70b-instruct:free", "name": "LLaMA 3.3 70B (Free Tier)"},
            {"id": "google/gemini-2.0-flash-exp:free", "name": "Gemini 2.0 Flash (Free Tier)"},
            {"id": "deepseek/deepseek-r1", "name": "DeepSeek R1 (Reasoning)"},
            {"id": "deepseek/deepseek-chat", "name": "DeepSeek V3 (Chat)"},
            {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini"},
            {"id": "anthropic/claude-3.5-sonnet", "name": "Claude 3.5 Sonnet"},
        ],
        "default_model": "meta-llama/llama-3.3-70b-instruct:free",
        "base_url": "https://openrouter.ai/api/v1",
        "requires_key": True,
        "key_env_var": "OPENROUTER_API_KEY",
        "doc_url": "https://openrouter.ai/keys"
    },
    "custom": {
        "id": "custom",
        "name": "Custom OpenAI-Compatible Endpoint",
        "badge": "Fleksibel",
        "description": "Hubungkan ke server LM Studio, LocalAI, vLLM, atau API kompatibel lainnya",
        "models": [
            {"id": "custom-model", "name": "Custom Model"}
        ],
        "default_model": "custom-model",
        "base_url": "http://localhost:1234/v1",
        "requires_key": True,
        "doc_url": "https://lmstudio.ai"
    }
}

class AIBrainManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._conversation_history: List[Dict[str, str]] = []

    def get_active_provider_config(self) -> Dict[str, Any]:
        """Mengambil konfigurasi provider AI yang aktif saat ini dari settings.json & .env."""
        settings = settings_manager.get_settings()
        ai_cfg = settings.get("ai_provider_config", {})
        
        provider_id = ai_cfg.get("provider", "gemini")
        if provider_id not in SUPPORTED_PROVIDERS:
            provider_id = "gemini"
            
        provider_meta = SUPPORTED_PROVIDERS[provider_id]
        model_id = ai_cfg.get("model") or provider_meta.get("default_model")
        
        # Cari API key dari settings, fallback ke .env
        api_keys = ai_cfg.get("api_keys", {})
        api_key = api_keys.get(provider_id, "")
        if not api_key and provider_meta.get("key_env_var"):
            api_key = os.getenv(provider_meta["key_env_var"], "")
            
        # Base URL untuk OpenAI-compatible providers
        base_url = ai_cfg.get("base_urls", {}).get(provider_id) or provider_meta.get("base_url", "")
        temperature = float(ai_cfg.get("temperature", 0.7))
        custom_system_prompt = ai_cfg.get("system_prompt") or DEFAULT_SYSTEM_INSTRUCTION

        return {
            "provider": provider_id,
            "model": model_id,
            "api_key": api_key,
            "base_url": base_url,
            "temperature": temperature,
            "system_prompt": custom_system_prompt,
            "meta": provider_meta
        }

    def get_full_system_instruction(self, base_prompt: str) -> str:
        """Menggabungkan instruksi sistem kepribadian kucing dengan konteks memori pengguna dan status Google Workspace."""
        memory_context = user_memory_manager.get_memory_context_string()
        
        # Konteks Google Workspace
        google_context = ""
        auth_status = google_auth_manager.get_auth_status()
        if auth_status.get("connected"):
            u = auth_status.get("user") or {}
            google_context = (
                f"\n[Konteks Google Workspace]: Akun Google terhubung atas nama {u.get('name')} ({u.get('email')}). "
                "Sebagai asisten Kitty yang pintar, kamu memiliki integrasi dengan Google Calendar, Google Tasks, dan Gmail pengguna."
            )
        else:
            google_context = (
                "\n[Konteks Google Workspace]: Akun Google belum terhubung. "
                "Jika pengguna meminta untuk melihat/mengatur kalender, tugas, atau email, ingatkan secara manis bahwa mereka dapat menghubungkan akun di menu Pengaturan > Google & Workspace."
            )

        return f"{base_prompt}\n{memory_context}\n{google_context}"

    def _resolve_realtime_workspace_data(self, prompt_text: str) -> str:
        """Mengecek apakah prompt memerlukan data Google Calendar, Tasks, atau Gmail, lalu mengambilnya secara realtime."""
        lower_p = prompt_text.lower()
        auth_status = google_auth_manager.get_auth_status()
        is_connected = auth_status.get("connected", False)

        # Kata kunci Calendar
        calendar_keywords = ["jadwal", "agenda", "kalender", "calendar", "acara hari ini", "jadwal besok", "agenda mendatang", "jadwal kuliah", "jadwal kerja"]
        # Kata kunci Tasks
        task_keywords = ["task", "tugas", "to-do", "todo", "daftar tugas", "catat to-do", "tugas hari ini", "list tugas"]
        # Kata kunci Gmail
        gmail_keywords = ["email", "gmail", "pesan masuk", "inbox", "cek email", "surat baru", "unread email"]

        injected_data = []

        if any(kw in lower_p for kw in calendar_keywords):
            if is_connected:
                cal_res = google_workspace.get_upcoming_events(max_results=5, days_ahead=7)
                if cal_res.get("success"):
                    events = cal_res.get("events", [])
                    if events:
                        ev_list_str = "\n".join([f"- {e['summary']} (Mulai: {e['start']}, Lokasi: {e['location'] or '-'})" for e in events])
                        injected_data.append(f"[DATA REALTIME GOOGLE CALENDAR]:\n{ev_list_str}")
                    else:
                        injected_data.append("[DATA REALTIME GOOGLE CALENDAR]: Tidak ada agenda mendatang dalam 7 hari ke depan.")
                else:
                    injected_data.append(f"[DATA REALTIME GOOGLE CALENDAR ERROR]: {cal_res.get('error')}")

        if any(kw in lower_p for kw in task_keywords):
            if is_connected:
                task_res = google_workspace.get_tasks(show_completed=False, max_results=8)
                if task_res.get("success"):
                    tasks = task_res.get("tasks", [])
                    if tasks:
                        t_list_str = "\n".join([f"- {t['title']} (Catatan: {t['notes'] or '-'}, Deadline: {t['due'] or '-'})" for t in tasks])
                        injected_data.append(f"[DATA REALTIME GOOGLE TASKS]:\n{t_list_str}")
                    else:
                        injected_data.append("[DATA REALTIME GOOGLE TASKS]: Semua tugas sudah selesai / daftar tugas kosong.")
                else:
                    injected_data.append(f"[DATA REALTIME GOOGLE TASKS ERROR]: {task_res.get('error')}")

        if any(kw in lower_p for kw in gmail_keywords):
            if is_connected:
                mail_res = google_workspace.get_unread_emails(max_results=5)
                if mail_res.get("success"):
                    emails = mail_res.get("emails", [])
                    if emails:
                        m_list_str = "\n".join([f"- Dari: {m['from']} | Subjek: {m['subject']} | Ringkasan: {m['snippet']}" for m in emails])
                        injected_data.append(f"[DATA REALTIME GMAIL UNREAD]:\nTotal belum dibaca: {mail_res.get('total_unread_estimate', len(emails))} email\n{m_list_str}")
                    else:
                        injected_data.append("[DATA REALTIME GMAIL UNREAD]: Tidak ada email baru yang belum dibaca di Inbox.")
                else:
                    injected_data.append(f"[DATA REALTIME GMAIL ERROR]: {mail_res.get('error')}")

        if injected_data:
            return prompt_text + "\n\n" + "\n\n".join(injected_data)
        return prompt_text

    def reset_chat_session(self):
        """Mereset riwayat percakapan sesi aktif."""
        with self._lock:
            self._conversation_history.clear()
            print("[AIBrain] Riwayat percakapan direset.")

    def _trigger_memory_extraction(self, prompt_text: str, response_text: str):
        """Memicu ekstraksi fakta baru secara asinkron di background thread."""
        def on_memories_updated(updated_memories):
            ws_manager.broadcast_threadsafe("memory_updated", updated_memories)

        user_memory_manager.extract_facts_async(
            prompt_text=prompt_text,
            response_text=response_text,
            on_updated_callback=on_memories_updated
        )

    # -------------------------------------------------------------
    # Provider: Google Gemini
    # -------------------------------------------------------------
    def _chat_gemini_stream(self, cfg: Dict[str, Any], prompt_text: str, chunk_callback: Optional[Callable[[str], None]]) -> str:
        import google.generativeai as genai
        
        api_key = cfg["api_key"]
        if not api_key:
            err_msg = "Google Gemini API Key belum diisi! Silakan masukkan API Key di Pengaturan > Model AI."
            if chunk_callback:
                chunk_callback(err_msg)
            return err_msg

        genai.configure(api_key=api_key)
        full_instruction = self.get_full_system_instruction(cfg["system_prompt"])
        
        try:
            model = genai.GenerativeModel(
                model_name=cfg["model"],
                system_instruction=full_instruction,
                generation_config=genai.types.GenerationConfig(
                    temperature=cfg["temperature"]
                )
            )
            
            # Format history untuk Gemini SDK
            gemini_history = []
            for msg in self._conversation_history:
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg["content"]]})

            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(prompt_text, stream=True)
            
            full_text = ""
            for chunk in response:
                try:
                    if chunk.text:
                        full_text += chunk.text
                        if chunk_callback:
                            chunk_callback(chunk.text)
                except Exception:
                    pass

            # Simpan ke conversation history
            self._conversation_history.append({"role": "user", "content": prompt_text})
            self._conversation_history.append({"role": "assistant", "content": full_text})
            
            self._trigger_memory_extraction(prompt_text, full_text)
            return full_text
        except Exception as e:
            err_msg = f"Gemini Error: {str(e)}"
            print(f"[Gemini Stream Error] {err_msg}")
            if chunk_callback:
                chunk_callback(err_msg)
            return err_msg

    # -------------------------------------------------------------
    # Provider: OpenAI Compatible (OpenAI, Groq, DeepSeek, Ollama, Custom)
    # -------------------------------------------------------------
    def _chat_openai_compatible_stream(self, cfg: Dict[str, Any], prompt_text: str, chunk_callback: Optional[Callable[[str], None]]) -> str:
        base_url = cfg["base_url"].rstrip("/")
        api_key = cfg["api_key"]
        
        if cfg["meta"].get("requires_key", True) and not api_key:
            err_msg = f"API Key untuk {cfg['meta']['name']} belum diisi! Silakan masukkan API Key di Pengaturan > Model AI."
            if chunk_callback:
                chunk_callback(err_msg)
            return err_msg

        headers = {
            "Content-Type": "application/json",
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        if "openrouter" in base_url.lower() or cfg.get("provider") == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/IlhamFatahillahR27/pet-assistant"
            headers["X-Title"] = "Pet Assistant Desktop"

        full_instruction = self.get_full_system_instruction(cfg["system_prompt"])
        
        messages = [{"role": "system", "content": full_instruction}]
        for msg in self._conversation_history[-10:]:  # Keep last 10 messages context
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": prompt_text})

        payload = {
            "model": cfg["model"],
            "messages": messages,
            "temperature": cfg["temperature"],
            "stream": True
        }

        endpoint = f"{base_url}/chat/completions"
        full_text = ""

        try:
            with httpx.Client(timeout=60.0) as client:
                with client.stream("POST", endpoint, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        err_body = response.read().decode("utf-8", errors="ignore")
                        err_msg = f"Error dari {cfg['meta']['name']} ({response.status_code}): {err_body}"
                        if chunk_callback:
                            chunk_callback(err_msg)
                        return err_msg

                    for line in response.iter_lines():
                        if not line:
                            continue
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                data_json = json.loads(data_str)
                                delta = data_json.get("choices", [{}])[0].get("delta", {})
                                chunk = delta.get("content", "")
                                if chunk:
                                    full_text += chunk
                                    if chunk_callback:
                                        chunk_callback(chunk)
                            except Exception:
                                continue

            self._conversation_history.append({"role": "user", "content": prompt_text})
            self._conversation_history.append({"role": "assistant", "content": full_text})
            
            self._trigger_memory_extraction(prompt_text, full_text)
            return full_text
        except Exception as e:
            err_msg = f"Koneksi {cfg['meta']['name']} Error: {str(e)}"
            print(f"[OpenAI-Compat Stream Error] {err_msg}")
            if chunk_callback:
                chunk_callback(err_msg)
            return err_msg

    # -------------------------------------------------------------
    # Public Router Methods
    # -------------------------------------------------------------
    def send_prompt_request_stream(self, prompt_text: str, chunk_callback: Optional[Callable[[str], None]] = None) -> str:
        """Router utama untuk mengirim prompt dan menerima stream chunk demi chunk."""
        with self._lock:
            # 1. Perkaya prompt jika terdapat pertanyaan terkait Google Workspace
            enriched_prompt = self._resolve_realtime_workspace_data(prompt_text)
            
            cfg = self.get_active_provider_config()
            provider = cfg["provider"]

            print(f"[AIBrain] Routing request ke provider '{provider}' dengan model '{cfg['model']}'")

            if provider == "gemini":
                return self._chat_gemini_stream(cfg, enriched_prompt, chunk_callback)
            else:
                return self._chat_openai_compatible_stream(cfg, enriched_prompt, chunk_callback)

    def send_prompt_request(self, prompt_text: str) -> str:
        """Mengirim prompt secara synchronous dan mengembalikan respon lengkap."""
        return self.send_prompt_request_stream(prompt_text, chunk_callback=None)

    def test_provider_connection(self, provider_id: str, model_id: str, api_key: str = "", base_url: str = "") -> Dict[str, Any]:
        """Menguji kredensial & koneksi ke provider AI tertentu."""
        if provider_id not in SUPPORTED_PROVIDERS:
            return {"success": False, "error": f"Provider '{provider_id}' tidak dikenal."}

        meta = SUPPORTED_PROVIDERS[provider_id]
        target_model = model_id or meta.get("default_model")
        target_base_url = base_url or meta.get("base_url", "")
        test_prompt = "Hai Kitty, berikan balasan singkat 1 kalimat sebagai tes koneksi!"

        try:
            if provider_id == "gemini":
                import google.generativeai as genai
                if not api_key:
                    api_key = os.getenv(meta.get("key_env_var", ""), "")
                if not api_key:
                    return {"success": False, "error": "API Key Gemini belum diisi."}
                
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(target_model)
                resp = model.generate_content(test_prompt)
                return {
                    "success": True,
                    "response": resp.text.strip() if resp else "OK",
                    "provider": provider_id,
                    "model": target_model
                }
            else:
                headers = {"Content-Type": "application/json"}
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                elif meta.get("requires_key", True):
                    api_key = os.getenv(meta.get("key_env_var", ""), "")
                    if api_key:
                        headers["Authorization"] = f"Bearer {api_key}"

                if "openrouter" in target_base_url.lower() or provider_id == "openrouter":
                    headers["HTTP-Referer"] = "https://github.com/IlhamFatahillahR27/pet-assistant"
                    headers["X-Title"] = "Pet Assistant Desktop"

                payload = {
                    "model": target_model,
                    "messages": [{"role": "user", "content": test_prompt}],
                    "max_tokens": 60
                }

                endpoint = f"{target_base_url.rstrip('/')}/chat/completions"
                with httpx.Client(timeout=15.0) as client:
                    res = client.post(endpoint, headers=headers, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        reply = data.get("choices", [{}])[0].get("message", {}).get("content", "Koneksi berhasil!")
                        return {"success": True, "response": reply, "provider": provider_id, "model": target_model}
                    else:
                        return {"success": False, "error": f"HTTP {res.status_code}: {res.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def fetch_ollama_local_models(self, base_url: str = "http://localhost:11434") -> List[Dict[str, Any]]:
        """Mengecek model apa saja yang sudah terpasang di instance Ollama lokal."""
        try:
            url = f"{base_url.rstrip('/')}/api/tags"
            with httpx.Client(timeout=5.0) as client:
                res = client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    models = []
                    for item in data.get("models", []):
                        name = item.get("name", "")
                        size_gb = round(item.get("size", 0) / (1024 ** 3), 2)
                        models.append({
                            "id": name,
                            "name": f"{name} ({size_gb} GB)" if size_gb > 0 else name
                        })
                    return models
        except Exception as e:
            print(f"[Ollama Probe Error] {e}")
        return []

# Singleton instance
ai_brain = AIBrainManager()
