import base64
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import httpx

from google_auth_manager import google_auth_manager


class GoogleWorkspaceService:
    """Klien RESTful untuk layanan Google Workspace (Calendar, Tasks, Gmail)."""

    def _get_headers(self) -> Optional[Dict[str, str]]:
        """Mendapatkan headers dengan Bearer Access Token yang valid."""
        token = google_auth_manager.get_valid_access_token()
        if not token:
            return None
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    # =========================================================================
    # 📅 GOOGLE CALENDAR
    # =========================================================================

    def get_upcoming_events(self, max_results: int = 5, days_ahead: int = 7) -> Dict[str, Any]:
        """Mengambil daftar kegiatan/agenda mendatang dari Google Calendar primer."""
        headers = self._get_headers()
        if not headers:
            return {"success": False, "error": "Akun Google belum terhubung atau token tidak valid."}

        now = datetime.now(timezone.utc)
        time_min = now.isoformat()
        time_max = (now + timedelta(days=days_ahead)).isoformat()

        url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
        params = {
            "timeMin": time_min,
            "timeMax": time_max,
            "singleEvents": "true",
            "orderBy": "startTime",
            "maxResults": max_results
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.get(url, headers=headers, params=params)
                if res.status_code != 200:
                    return {"success": False, "error": f"Calendar API error ({res.status_code}): {res.text}"}

                data = res.json()
                items = data.get("items", [])
                events = []
                for item in items:
                    start = item.get("start", {})
                    end = item.get("end", {})
                    events.append({
                        "id": item.get("id", ""),
                        "summary": item.get("summary", "(Tanpa Judul)"),
                        "description": item.get("description", ""),
                        "location": item.get("location", ""),
                        "start": start.get("dateTime") or start.get("date", ""),
                        "end": end.get("dateTime") or end.get("date", ""),
                        "htmlLink": item.get("htmlLink", "")
                    })
                return {"success": True, "events": events, "count": len(events)}
        except Exception as e:
            return {"success": False, "error": f"Exception get_events: {str(e)}"}

    def create_calendar_event(
        self,
        summary: str,
        start_iso: str,
        end_iso: Optional[str] = None,
        description: str = "",
        location: str = ""
    ) -> Dict[str, Any]:
        """Menambahkan kegiatan/agenda baru ke Google Calendar primer."""
        headers = self._get_headers()
        if not headers:
            return {"success": False, "error": "Akun Google belum terhubung atau token tidak valid."}

        # Jika end_iso tidak diberikan, jadwalkan durasi 1 jam secara default
        if not end_iso:
            try:
                dt_start = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
                dt_end = dt_start + timedelta(hours=1)
                end_iso = dt_end.isoformat()
            except Exception:
                end_iso = start_iso

        payload = {
            "summary": summary,
            "description": description,
            "location": location,
            "start": {"dateTime": start_iso} if "T" in start_iso else {"date": start_iso},
            "end": {"dateTime": end_iso} if "T" in end_iso else {"date": end_iso},
        }

        url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code in [200, 201]:
                    created = res.json()
                    return {
                        "success": True,
                        "event": {
                            "id": created.get("id"),
                            "summary": created.get("summary"),
                            "start": created.get("start", {}),
                            "htmlLink": created.get("htmlLink", "")
                        }
                    }
                else:
                    return {"success": False, "error": f"Gagal membuat event ({res.status_code}): {res.text}"}
        except Exception as e:
            return {"success": False, "error": f"Exception create_event: {str(e)}"}

    def delete_calendar_event(self, event_id: str) -> Dict[str, Any]:
        """Menghapus agenda dari Google Calendar primer."""
        headers = self._get_headers()
        if not headers:
            return {"success": False, "error": "Akun Google belum terhubung."}

        url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}"
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.delete(url, headers=headers)
                if res.status_code in [200, 204]:
                    return {"success": True, "message": "Event berhasil dihapus."}
                else:
                    return {"success": False, "error": f"Gagal hapus event ({res.status_code}): {res.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # ✅ GOOGLE TASKS
    # =========================================================================

    def get_tasks(self, show_completed: bool = False, max_results: int = 15) -> Dict[str, Any]:
        """Mengambil daftar tugas to-do list dari Google Tasks default."""
        headers = self._get_headers()
        if not headers:
            return {"success": False, "error": "Akun Google belum terhubung atau token tidak valid."}

        url = "https://tasks.googleapis.com/tasks/v1/lists/@default/tasks"
        params = {
            "showCompleted": str(show_completed).lower(),
            "showHidden": "false",
            "maxResults": max_results
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.get(url, headers=headers, params=params)
                if res.status_code != 200:
                    return {"success": False, "error": f"Tasks API error ({res.status_code}): {res.text}"}

                data = res.json()
                items = data.get("items", [])
                tasks = []
                for item in items:
                    tasks.append({
                        "id": item.get("id", ""),
                        "title": item.get("title", "(Tanpa Judul)"),
                        "notes": item.get("notes", ""),
                        "status": item.get("status", "needsAction"),
                        "due": item.get("due", ""),
                        "updated": item.get("updated", "")
                    })
                return {"success": True, "tasks": tasks, "count": len(tasks)}
        except Exception as e:
            return {"success": False, "error": f"Exception get_tasks: {str(e)}"}

    def create_task(self, title: str, notes: str = "", due_iso: Optional[str] = None) -> Dict[str, Any]:
        """Menambahkan tugas baru ke Google Tasks default."""
        headers = self._get_headers()
        if not headers:
            return {"success": False, "error": "Akun Google belum terhubung atau token tidak valid."}

        payload: Dict[str, Any] = {
            "title": title,
            "notes": notes,
        }
        if due_iso:
            payload["due"] = due_iso

        url = "https://tasks.googleapis.com/tasks/v1/lists/@default/tasks"
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code in [200, 201]:
                    task = res.json()
                    return {
                        "success": True,
                        "task": {
                            "id": task.get("id"),
                            "title": task.get("title"),
                            "status": task.get("status", "needsAction")
                        }
                    }
                else:
                    return {"success": False, "error": f"Gagal membuat task ({res.status_code}): {res.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def complete_task(self, task_id: str) -> Dict[str, Any]:
        """Menandai tugas sebagai selesai di Google Tasks."""
        headers = self._get_headers()
        if not headers:
            return {"success": False, "error": "Akun Google belum terhubung."}

        url = f"https://tasks.googleapis.com/tasks/v1/lists/@default/tasks/{task_id}"
        payload = {"status": "completed"}

        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.patch(url, headers=headers, json=payload)
                if res.status_code in [200, 204]:
                    return {"success": True, "message": "Tugas berhasil diselesaikan."}
                else:
                    return {"success": False, "error": f"Gagal menyelesaikan task ({res.status_code}): {res.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Menghapus tugas dari Google Tasks."""
        headers = self._get_headers()
        if not headers:
            return {"success": False, "error": "Akun Google belum terhubung."}

        url = f"https://tasks.googleapis.com/tasks/v1/lists/@default/tasks/{task_id}"
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.delete(url, headers=headers)
                if res.status_code in [200, 204]:
                    return {"success": True, "message": "Tugas berhasil dihapus."}
                else:
                    return {"success": False, "error": f"Gagal menghapus task ({res.status_code}): {res.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # ✉️ GMAIL
    # =========================================================================

    def get_unread_emails(self, max_results: int = 5) -> Dict[str, Any]:
        """Mengambil daftar email belum dibaca dari Inbox Gmail pengguna."""
        headers = self._get_headers()
        if not headers:
            return {"success": False, "error": "Akun Google belum terhubung atau token tidak valid."}

        list_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
        params = {
            "q": "is:unread in:inbox",
            "maxResults": max_results
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.get(list_url, headers=headers, params=params)
                if res.status_code != 200:
                    return {"success": False, "error": f"Gmail API list error ({res.status_code}): {res.text}"}

                list_data = res.json()
                messages_meta = list_data.get("messages", [])
                result_size_estimate = list_data.get("resultSizeEstimate", len(messages_meta))

                emails = []
                for item in messages_meta:
                    msg_id = item.get("id")
                    msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}"
                    msg_params = {
                        "format": "metadata",
                        "metadataHeaders": ["Subject", "From", "Date"]
                    }
                    msg_res = client.get(msg_url, headers=headers, params=msg_params)
                    if msg_res.status_code == 200:
                        msg_data = msg_res.json()
                        headers_list = msg_data.get("payload", {}).get("headers", [])
                        
                        subject = "(Tanpa Subjek)"
                        sender = "Tidak Diketahui"
                        date_str = ""
                        for h in headers_list:
                            name = h.get("name", "").lower()
                            if name == "subject":
                                subject = h.get("value", subject)
                            elif name == "from":
                                sender = h.get("value", sender)
                            elif name == "date":
                                date_str = h.get("value", date_str)

                        emails.append({
                            "id": msg_id,
                            "threadId": msg_data.get("threadId", ""),
                            "subject": subject,
                            "from": sender,
                            "date": date_str,
                            "snippet": msg_data.get("snippet", "")
                        })

                return {
                    "success": True,
                    "emails": emails,
                    "count": len(emails),
                    "total_unread_estimate": result_size_estimate
                }
        except Exception as e:
            return {"success": False, "error": f"Exception get_unread_emails: {str(e)}"}

    def send_email(self, to_email: str, subject: str, body_text: str) -> Dict[str, Any]:
        """Mengirim email melalui Gmail API pengguna."""
        headers = self._get_headers()
        if not headers:
            return {"success": False, "error": "Akun Google belum terhubung atau token tidak valid."}

        try:
            mime_message = MIMEText(body_text, "plain", "utf-8")
            mime_message["to"] = to_email
            mime_message["subject"] = subject

            # URL-safe Base64 encoding
            raw_encoded = base64.urlsafe_b64encode(mime_message.as_bytes()).decode("utf-8")
            payload = {"raw": raw_encoded}

            url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code in [200, 201]:
                    data = res.json()
                    return {"success": True, "message_id": data.get("id"), "thread_id": data.get("threadId")}
                else:
                    return {"success": False, "error": f"Gagal mengirim email ({res.status_code}): {res.text}"}
        except Exception as e:
            return {"success": False, "error": f"Exception send_email: {str(e)}"}


# Singleton instance
google_workspace = GoogleWorkspaceService()
