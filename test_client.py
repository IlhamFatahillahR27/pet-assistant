import time
import json
import urllib.request
import urllib.error
import asyncio
import websockets

BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws"

def test_rest_endpoints():
    print("--- 1. Testing GET /health ---")
    req = urllib.request.Request(f"{BASE_URL}/health")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print(f"Health Response: {data}")
        assert data.get("status") == "online", "Health check failed!"

    print("\n--- 2. Testing GET /api/settings ---")
    req = urllib.request.Request(f"{BASE_URL}/api/settings")
    with urllib.request.urlopen(req) as resp:
        settings = json.loads(resp.read().decode())
        print(f"Settings: {settings}")
        assert "ai_model" in settings, "Settings missing ai_model!"

    print("\n--- 3. Testing PUT /api/settings ---")
    update_payload = json.dumps({"tts": {"rate": 170}}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/api/settings",
        data=update_payload,
        headers={"Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req) as resp:
        updated = json.loads(resp.read().decode())
        print(f"Updated Settings: {updated}")
        assert updated.get("settings", {}).get("tts", {}).get("rate") == 170, "Settings update failed!"

    print("\n--- 4. Testing GET /api/tts/voices ---")
    req = urllib.request.Request(f"{BASE_URL}/api/tts/voices")
    with urllib.request.urlopen(req) as resp:
        voices = json.loads(resp.read().decode())
        print(f"Total Voices Available: {len(voices.get('voices', []))}")
        assert "voices" in voices, "Voices response invalid!"

    print("\n--- 5. Testing POST /api/chat ---")
    chat_payload = json.dumps({"prompt": "Halo, sapa aku dengan singkat!"}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/api/chat",
        data=chat_payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        chat_resp = json.loads(resp.read().decode())
        print(f"Gemini Response: {chat_resp.get('response')}")
        assert "response" in chat_resp, "Chat response missing!"

    print("\n[OK] Semua REST API Test BERHASIL!\n")

async def test_websocket():
    print("--- 6. Testing WebSocket Connection & Messages ---")
    async with websockets.connect(WS_URL) as websocket:
        # Receive welcome event
        greeting = await websocket.recv()
        greeting_data = json.loads(greeting)
        print(f"WS Received: {greeting_data}")
        assert greeting_data.get("event") == "connected", "WS connection event failed!"

        # Send ping
        print("Sending ping...")
        await websocket.send(json.dumps({"action": "ping"}))
        pong = await websocket.recv()
        pong_data = json.loads(pong)
        print(f"WS Received: {pong_data}")
        assert pong_data.get("event") == "pong", "WS ping-pong failed!"

        # Send chat action via WS
        print("Sending chat prompt via WS...")
        await websocket.send(json.dumps({"action": "chat", "prompt": "Halo Meow!"}))
        
        # Listen for streaming chunks
        received_chunks = []
        for _ in range(10):
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                chunk_data = json.loads(msg)
                print(f"WS Event Received: {chunk_data}")
                if chunk_data.get("event") == "chat_chunk":
                    received_chunks.append(chunk_data)
                    if chunk_data.get("data", {}).get("done"):
                        print("Streaming selesei!")
                        break
            except asyncio.TimeoutError:
                print("WS recv timeout!")
                break
        
        assert len(received_chunks) > 0, "No chat chunks received via WS!"

    print("\n[OK] Semua WebSocket Test BERHASIL!\n")

def run_tests():
    try:
        test_rest_endpoints()
        asyncio.run(test_websocket())
        print("[SUCCESS] SELURUH PENGUJIAN FASE 2 BERHASIL 100%!")
    except Exception as e:
        print(f"\n[ERROR] PENGUJIAN GAGAL: {e}")

if __name__ == "__main__":
    run_tests()
