const BASE_URL = 'http://127.0.0.1:8000';

export async function fetchHealth() {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    return await res.json();
  } catch (err) {
    console.error('Health check error:', err);
    return { status: 'offline' };
  }
}

export async function fetchSettings() {
  try {
    const res = await fetch(`${BASE_URL}/api/settings`);
    return await res.json();
  } catch (err) {
    console.error('Fetch settings error:', err);
    return null;
  }
}

export async function updateSettings(settings) {
  try {
    const res = await fetch(`${BASE_URL}/api/settings`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings),
    });
    return await res.json();
  } catch (err) {
    console.error('Update settings error:', err);
    return null;
  }
}

export async function sendChatMessage(prompt) {
  try {
    const res = await fetch(`${BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    });
    return await res.json();
  } catch (err) {
    console.error('Send chat error:', err);
    return { error: err.message };
  }
}

export async function triggerSTT() {
  try {
    const res = await fetch(`${BASE_URL}/api/stt/listen`, { method: 'POST' });
    return await res.json();
  } catch (err) {
    console.error('Trigger STT error:', err);
    return null;
  }
}

export async function triggerTTS(text, rate = 170) {
  try {
    const res = await fetch(`${BASE_URL}/api/tts/speak`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, rate }),
    });
    return await res.json();
  } catch (err) {
    console.error('Trigger TTS error:', err);
    return null;
  }
}

export async function startWakeWord() {
  try {
    const res = await fetch(`${BASE_URL}/api/wakeword/start`, { method: 'POST' });
    return await res.json();
  } catch (err) {
    console.error('Start wake word error:', err);
    return null;
  }
}

export async function stopWakeWord() {
  try {
    const res = await fetch(`${BASE_URL}/api/wakeword/stop`, { method: 'POST' });
    return await res.json();
  } catch (err) {
    console.error('Stop wake word error:', err);
    return null;
  }
}
