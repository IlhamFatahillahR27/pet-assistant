import sys
import os

# Set UTF-8 stdout
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_routes():
    print("\n--- [TEST] FastAPI REST Routes ---")
    
    # 1. Health Check
    res = client.get("/health")
    assert res.status_code == 200
    print("[PASS] GET /health ->", res.json())

    # 2. Settings
    res = client.get("/api/settings")
    assert res.status_code == 200
    print("[PASS] GET /api/settings")

    # 3. Google Status
    res = client.get("/api/google/status")
    assert res.status_code == 200
    data = res.json()
    print("[PASS] GET /api/google/status -> connected:", data.get("connected"))

    # 4. Google Auth URL
    res = client.get("/api/google/auth-url")
    assert res.status_code == 200
    assert "auth_url" in res.json()
    print("[PASS] GET /api/google/auth-url")

    # 5. Google Workspace Endpoints (expect 400 when unauthenticated)
    res_cal = client.get("/api/google/calendar/events")
    assert res_cal.status_code == 400
    print("[PASS] GET /api/google/calendar/events (Graceful 400 on unauthenticated)")

    res_tasks = client.get("/api/google/tasks")
    assert res_tasks.status_code == 400
    print("[PASS] GET /api/google/tasks (Graceful 400 on unauthenticated)")

    res_gmail = client.get("/api/google/gmail/unread")
    assert res_gmail.status_code == 400
    print("[PASS] GET /api/google/gmail/unread (Graceful 400 on unauthenticated)")

    # 6. Google Logout
    res_logout = client.post("/api/google/logout")
    assert res_logout.status_code == 200
    print("[PASS] POST /api/google/logout")

    print("\n[ALL PASS] ALL FASTAPI ROUTE TESTS PASSED!")

if __name__ == "__main__":
    test_routes()
