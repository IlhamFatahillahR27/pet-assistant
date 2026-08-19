import sys
import os

# Set UTF-8 encoding for Windows stdout
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(__file__))

from google_auth_manager import google_auth_manager
from google_workspace import google_workspace
from ai_brain import ai_brain
from settings_manager import settings_manager

def test_google_auth_manager():
    print("\n--- [TEST] GoogleAuthManager ---")
    status = google_auth_manager.get_auth_status()
    print("Initial Auth Status:", status)
    assert isinstance(status, dict)
    assert "connected" in status
    assert "configured" in status

    # Test settings update with Client ID & Secret
    settings_manager.update_settings({
        "google_oauth": {
            "client_id": "test_client_id.apps.googleusercontent.com",
            "client_secret": "test_client_secret"
        }
    })
    
    assert google_auth_manager.is_configured() == True
    auth_url_res = google_auth_manager.generate_auth_url()
    print("Auth URL Result:", auth_url_res)
    assert auth_url_res.get("success") == True
    assert "accounts.google.com" in auth_url_res.get("auth_url", "")
    assert "redirect_uri" in auth_url_res.get("auth_url", "")
    assert "scope" in auth_url_res.get("auth_url", "")
    print("[PASS] GoogleAuthManager tests passed!")

def test_google_workspace_unauthenticated_handling():
    print("\n--- [TEST] GoogleWorkspace Service (Unauthenticated Handling) ---")
    cal_res = google_workspace.get_upcoming_events()
    print("Calendar unauthenticated response:", cal_res)
    assert cal_res.get("success") == False
    assert "belum terhubung" in cal_res.get("error", "").lower()

    tasks_res = google_workspace.get_tasks()
    print("Tasks unauthenticated response:", tasks_res)
    assert tasks_res.get("success") == False

    gmail_res = google_workspace.get_unread_emails()
    print("Gmail unauthenticated response:", gmail_res)
    assert gmail_res.get("success") == False
    print("[PASS] GoogleWorkspace unauthenticated handling tests passed!")

def test_ai_brain_workspace_enrichment():
    print("\n--- [TEST] AIBrain Workspace Resolution & System Prompt ---")
    system_prompt = ai_brain.get_full_system_instruction("Default prompt")
    print("System Prompt snippet:\n", system_prompt[-200:])
    assert "Google Workspace" in system_prompt

    # Test keyword detection
    prompt_with_cal = "Kitty, apa saja agenda kegiatan di kalenderku?"
    enriched = ai_brain._resolve_realtime_workspace_data(prompt_with_cal)
    print("Enriched prompt for calendar:", enriched)

    prompt_with_tasks = "Tolong periksa apa ada task atau tugas hari ini?"
    enriched_tasks = ai_brain._resolve_realtime_workspace_data(prompt_with_tasks)
    print("Enriched prompt for tasks:", enriched_tasks)

    prompt_with_mail = "Apakah ada pesan masuk atau email baru di gmail?"
    enriched_mail = ai_brain._resolve_realtime_workspace_data(prompt_with_mail)
    print("Enriched prompt for email:", enriched_mail)
    print("[PASS] AIBrain workspace enrichment tests passed!")

if __name__ == "__main__":
    test_google_auth_manager()
    test_google_workspace_unauthenticated_handling()
    test_ai_brain_workspace_enrichment()
    print("\n[ALL PASS] ALL PHASE 8 BACKEND TESTS PASSED SUCCESSFULLY!")
