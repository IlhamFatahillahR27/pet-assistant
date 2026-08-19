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

export async function triggerTTS(text, rate = 170, volume = 1.0, voice_id = null) {
  try {
    const res = await fetch(`${BASE_URL}/api/tts/speak`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, rate, volume, voice_id }),
    });
    return await res.json();
  } catch (err) {
    console.error('Trigger TTS error:', err);
    return null;
  }
}

export async function fetchAvailableVoices() {
  try {
    const res = await fetch(`${BASE_URL}/api/tts/voices`);
    const data = await res.json();
    return data.voices || [];
  } catch (err) {
    console.error('Fetch voices error:', err);
    return [];
  }
}

export async function openSpeechSettings() {
  try {
    const res = await fetch(`${BASE_URL}/api/system/open-speech-settings`, { method: 'POST' });
    return await res.json();
  } catch (err) {
    console.error('Open speech settings error:', err);
    return null;
  }
}

export async function openExternalUrl(url) {
  try {
    const res = await fetch(`${BASE_URL}/api/system/open-browser`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    return await res.json();
  } catch (err) {
    console.error('Open external url error:', err);
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

export async function fetchMemories() {
  try {
    const res = await fetch(`${BASE_URL}/api/memories`);
    const data = await res.json();
    return data.memories || [];
  } catch (err) {
    console.error('Fetch memories error:', err);
    return [];
  }
}

export async function addMemory(fact, category = 'general') {
  try {
    const res = await fetch(`${BASE_URL}/api/memories`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fact, category }),
    });
    return await res.json();
  } catch (err) {
    console.error('Add memory error:', err);
    return null;
  }
}

export async function deleteMemory(memoryId) {
  try {
    const res = await fetch(`${BASE_URL}/api/memories/${memoryId}`, {
      method: 'DELETE',
    });
    return await res.json();
  } catch (err) {
    console.error('Delete memory error:', err);
    return null;
  }
}

export async function clearMemories() {
  try {
    const res = await fetch(`${BASE_URL}/api/memories`, {
      method: 'DELETE',
    });
    return await res.json();
  } catch (err) {
    console.error('Clear memories error:', err);
    return null;
  }
}

export async function fetchAIProviders() {
  try {
    const res = await fetch(`${BASE_URL}/api/ai/providers`);
    const data = await res.json();
    return data.providers || [];
  } catch (err) {
    console.error('Fetch AI providers error:', err);
    return [];
  }
}

export async function testAIConnection(provider, model = '', apiKey = '', baseUrl = '') {
  try {
    const res = await fetch(`${BASE_URL}/api/ai/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        provider,
        model,
        api_key: apiKey,
        base_url: baseUrl,
      }),
    });
    return await res.json();
  } catch (err) {
    console.error('Test AI connection error:', err);
    return { success: false, error: err.message };
  }
}

export async function fetchOllamaLocalModels(baseUrl = 'http://localhost:11434') {
  try {
    const encodedUrl = encodeURIComponent(baseUrl);
    const res = await fetch(`${BASE_URL}/api/ai/ollama/models?base_url=${encodedUrl}`);
    const data = await res.json();
    return data.models || [];
  } catch (err) {
    console.error('Fetch Ollama models error:', err);
    return [];
  }
}

// =========================================================
// GOOGLE OAUTH & GOOGLE WORKSPACE API CLIENTS
// =========================================================

export async function fetchGoogleStatus() {
  try {
    const res = await fetch(`${BASE_URL}/api/google/status`);
    return await res.json();
  } catch (err) {
    console.error('Fetch Google status error:', err);
    return { connected: false, configured: false, user: null, scopes: [] };
  }
}

export async function getGoogleAuthUrl() {
  try {
    const res = await fetch(`${BASE_URL}/api/google/auth-url`);
    return await res.json();
  } catch (err) {
    console.error('Get Google auth url error:', err);
    return { success: false, error: err.message };
  }
}

export async function logoutGoogle() {
  try {
    const res = await fetch(`${BASE_URL}/api/google/logout`, { method: 'POST' });
    return await res.json();
  } catch (err) {
    console.error('Logout Google error:', err);
    return { status: 'error', message: err.message };
  }
}

export async function saveGoogleConfig(clientId, clientSecret) {
  try {
    const res = await fetch(`${BASE_URL}/api/google/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ client_id: clientId, client_secret: clientSecret }),
    });
    return await res.json();
  } catch (err) {
    console.error('Save Google config error:', err);
    return { status: 'error', message: err.message };
  }
}

export async function fetchCalendarEvents(maxResults = 5, daysAhead = 7) {
  try {
    const res = await fetch(`${BASE_URL}/api/google/calendar/events?max_results=${maxResults}&days_ahead=${daysAhead}`);
    const data = await res.json();
    return data.events || [];
  } catch (err) {
    console.error('Fetch Calendar events error:', err);
    return [];
  }
}

export async function createCalendarEvent(summary, start, end = null, description = '', location = '') {
  try {
    const res = await fetch(`${BASE_URL}/api/google/calendar/events`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ summary, start, end, description, location }),
    });
    return await res.json();
  } catch (err) {
    console.error('Create Calendar event error:', err);
    return { success: false, error: err.message };
  }
}

export async function deleteCalendarEvent(eventId) {
  try {
    const res = await fetch(`${BASE_URL}/api/google/calendar/events/${eventId}`, {
      method: 'DELETE',
    });
    return await res.json();
  } catch (err) {
    console.error('Delete Calendar event error:', err);
    return { success: false, error: err.message };
  }
}

export async function fetchGoogleTasks(showCompleted = false, maxResults = 15) {
  try {
    const res = await fetch(`${BASE_URL}/api/google/tasks?show_completed=${showCompleted}&max_results=${maxResults}`);
    const data = await res.json();
    return data.tasks || [];
  } catch (err) {
    console.error('Fetch Google tasks error:', err);
    return [];
  }
}

export async function createGoogleTask(title, notes = '', due = null) {
  try {
    const res = await fetch(`${BASE_URL}/api/google/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, notes, due }),
    });
    return await res.json();
  } catch (err) {
    console.error('Create Google task error:', err);
    return { success: false, error: err.message };
  }
}

export async function completeGoogleTask(taskId) {
  try {
    const res = await fetch(`${BASE_URL}/api/google/tasks/${taskId}/complete`, {
      method: 'POST',
    });
    return await res.json();
  } catch (err) {
    console.error('Complete Google task error:', err);
    return { success: false, error: err.message };
  }
}

export async function deleteGoogleTask(taskId) {
  try {
    const res = await fetch(`${BASE_URL}/api/google/tasks/${taskId}`, {
      method: 'DELETE',
    });
    return await res.json();
  } catch (err) {
    console.error('Delete Google task error:', err);
    return { success: false, error: err.message };
  }
}

export async function fetchUnreadEmails(maxResults = 5) {
  try {
    const res = await fetch(`${BASE_URL}/api/google/gmail/unread?max_results=${maxResults}`);
    const data = await res.json();
    return data.emails || [];
  } catch (err) {
    console.error('Fetch unread emails error:', err);
    return [];
  }
}

export async function sendGmailEmail(to, subject, body) {
  try {
    const res = await fetch(`${BASE_URL}/api/google/gmail/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ to, subject, body }),
    });
    return await res.json();
  } catch (err) {
    console.error('Send Gmail error:', err);
    return { success: false, error: err.message };
  }
}



