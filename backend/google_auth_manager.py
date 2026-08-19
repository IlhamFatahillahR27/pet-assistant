import os
import json
import time
import urllib.parse
import threading
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv

from settings_manager import settings_manager
from ws_manager import ws_manager

load_dotenv()

TOKEN_FILE = os.path.join(os.path.dirname(__file__), "google_tokens.json")

# Default OAuth 2.0 Scopes yang dibutuhkan untuk Assistant & Google Workspace
DEFAULT_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
]

REDIRECT_URI = "http://127.0.0.1:8000/api/google/oauth/callback"


class GoogleAuthManager:
    """Mengelola alur Google OAuth 2.0, penyimpanan token persisten, dan auto-refresh token."""

    def __init__(self, token_file: str = TOKEN_FILE):
        self.token_file = token_file
        self._lock = threading.Lock()
        self._tokens: Dict[str, Any] = self._load_tokens()

    def _load_tokens(self) -> Dict[str, Any]:
        """Memuat token dari file lokal jika ada."""
        if not os.path.exists(self.token_file):
            return {}
        try:
            with open(self.token_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[GoogleAuthManager Error] Gagal membaca google_tokens.json: {e}")
            return {}

    def _save_tokens(self, tokens: Dict[str, Any]):
        """Menyimpan data token ke file JSON lokal."""
        try:
            with open(self.token_file, "w", encoding="utf-8") as f:
                json.dump(tokens, f, indent=2, ensure_ascii=False)
            self._tokens = tokens
        except Exception as e:
            print(f"[GoogleAuthManager Error] Gagal menyimpan google_tokens.json: {e}")

    def get_oauth_credentials(self) -> Dict[str, str]:
        """Mengambil Client ID dan Client Secret dari settings.json atau .env."""
        settings = settings_manager.get_settings()
        google_cfg = settings.get("google_oauth", {})
        
        client_id = (
            google_cfg.get("client_id")
            or os.getenv("GOOGLE_CLIENT_ID", "")
        ).strip()
        
        client_secret = (
            google_cfg.get("client_secret")
            or os.getenv("GOOGLE_CLIENT_SECRET", "")
        ).strip()

        return {
            "client_id": client_id,
            "client_secret": client_secret
        }

    def is_configured(self) -> bool:
        """Mengecek apakah Client ID dan Client Secret sudah diisi."""
        creds = self.get_oauth_credentials()
        return bool(creds["client_id"] and creds["client_secret"])

    def is_authenticated(self) -> bool:
        """Mengecek apakah user sudah login dan memiliki token valid/refreshable."""
        with self._lock:
            return bool(self._tokens.get("access_token") or self._tokens.get("refresh_token"))

    def generate_auth_url(self, state: str = "pet_assistant_auth") -> Dict[str, Any]:
        """Menghasilkan URL Google OAuth 2.0 consent authorization."""
        creds = self.get_oauth_credentials()
        client_id = creds["client_id"]

        if not client_id:
            return {
                "success": False,
                "error": "Google Client ID belum dikonfigurasi. Silakan masukkan Client ID di Pengaturan > Google & Workspace."
            }

        params = {
            "client_id": client_id,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(DEFAULT_SCOPES),
            "access_type": "offline",
            "prompt": "consent",
            "state": state
        }
        
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
        return {
            "success": True,
            "auth_url": auth_url
        }

    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Menukar authorization code menjadi access_token & refresh_token dari Google."""
        creds = self.get_oauth_credentials()
        client_id = creds["client_id"]
        client_secret = creds["client_secret"]

        if not client_id or not client_secret:
            return {"success": False, "error": "Client ID atau Client Secret tidak ditemukan."}

        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(token_url, data=payload)
                if res.status_code != 200:
                    err_detail = res.text
                    print(f"[GoogleAuthManager Error] Token exchange failed: {err_detail}")
                    return {"success": False, "error": f"HTTP {res.status_code}: {err_detail}"}

                token_data = res.json()
                access_token = token_data.get("access_token")
                refresh_token = token_data.get("refresh_token")
                expires_in = token_data.get("expires_in", 3600)
                expires_at = time.time() + expires_in

                # Ambil profil user dari UserInfo API
                profile = self._fetch_user_profile(access_token)

                with self._lock:
                    saved_data = {
                        "access_token": access_token,
                        "refresh_token": refresh_token or self._tokens.get("refresh_token", ""),
                        "expires_at": expires_at,
                        "token_type": token_data.get("token_type", "Bearer"),
                        "scope": token_data.get("scope", ""),
                        "user_profile": profile,
                        "updated_at": time.time()
                    }
                    self._save_tokens(saved_data)

                # Broadcast WebSocket event ke UI
                ws_manager.broadcast_threadsafe("google_auth_changed", self.get_auth_status())
                return {"success": True, "profile": profile}

        except Exception as e:
            print(f"[GoogleAuthManager Exception] {e}")
            return {"success": False, "error": str(e)}

    def _fetch_user_profile(self, access_token: str) -> Dict[str, str]:
        """Mengambil data profil nama, email, dan foto avatar dari Google UserInfo API."""
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                if res.status_code == 200:
                    data = res.json()
                    return {
                        "id": data.get("id", ""),
                        "email": data.get("email", ""),
                        "name": data.get("name", "Pengguna Google"),
                        "picture": data.get("picture", "")
                    }
        except Exception as e:
            print(f"[GoogleAuthManager] Gagal fetch userinfo: {e}")
        return {"name": "Pengguna Google", "email": "", "picture": ""}

    def get_valid_access_token(self) -> Optional[str]:
        """Mengembalikan access token yang valid. Jika kedaluwarsa, otomatis refresh token."""
        with self._lock:
            if not self._tokens.get("access_token"):
                return None

            expires_at = self._tokens.get("expires_at", 0)
            # Jika token masih berlaku lebih dari 2 menit ke depan, gunakan yang ada
            if time.time() < (expires_at - 120):
                return self._tokens.get("access_token")

            # Token kedaluwarsa atau segera kedaluwarsa, lakukan refresh token
            refresh_token = self._tokens.get("refresh_token")
            if not refresh_token:
                print("[GoogleAuthManager Warning] Access token kedaluwarsa dan tidak ada refresh token.")
                return None

            creds = self.get_oauth_credentials()
            token_url = "https://oauth2.googleapis.com/token"
            payload = {
                "client_id": creds["client_id"],
                "client_secret": creds["client_secret"],
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }

            try:
                with httpx.Client(timeout=15.0) as client:
                    res = client.post(token_url, data=payload)
                    if res.status_code == 200:
                        data = res.json()
                        new_access_token = data.get("access_token")
                        expires_in = data.get("expires_in", 3600)
                        
                        self._tokens["access_token"] = new_access_token
                        self._tokens["expires_at"] = time.time() + expires_in
                        if "refresh_token" in data:
                            self._tokens["refresh_token"] = data["refresh_token"]
                        self._tokens["updated_at"] = time.time()
                        
                        self._save_tokens(self._tokens)
                        print("[GoogleAuthManager] Access token berhasil di-refresh.")
                        return new_access_token
                    else:
                        print(f"[GoogleAuthManager Refresh Error] HTTP {res.status_code}: {res.text}")
                        return None
            except Exception as e:
                print(f"[GoogleAuthManager Refresh Exception] {e}")
                return None

    def get_auth_status(self) -> Dict[str, Any]:
        """Mengembalikan data status autentikasi Google saat ini untuk UI."""
        with self._lock:
            is_auth = bool(self._tokens.get("access_token") or self._tokens.get("refresh_token"))
            profile = self._tokens.get("user_profile", {})
            creds = self.get_oauth_credentials()
            
            return {
                "connected": is_auth,
                "configured": bool(creds["client_id"] and creds["client_secret"]),
                "client_id": creds["client_id"][:12] + "..." if creds["client_id"] else "",
                "user": {
                    "name": profile.get("name", "Belum Terhubung"),
                    "email": profile.get("email", ""),
                    "picture": profile.get("picture", "")
                } if is_auth else None,
                "scopes": self._tokens.get("scope", "").split() if is_auth else []
            }

    def logout(self) -> bool:
        """Memutuskan koneksi Google OAuth dan menghapus token lokal."""
        with self._lock:
            token = self._tokens.get("access_token") or self._tokens.get("refresh_token")
            if token:
                try:
                    with httpx.Client(timeout=5.0) as client:
                        client.post(
                            "https://oauth2.googleapis.com/revoke",
                            params={"token": token}
                        )
                except Exception as e:
                    print(f"[GoogleAuthManager Revoke Notice] {e}")

            self._tokens = {}
            if os.path.exists(self.token_file):
                try:
                    os.remove(self.token_file)
                except Exception as e:
                    print(f"[GoogleAuthManager Error] Gagal menghapus file token: {e}")

        # Broadcast WebSocket event ke UI
        ws_manager.broadcast_threadsafe("google_auth_changed", self.get_auth_status())
        return True


# Singleton instance
google_auth_manager = GoogleAuthManager()
