import React from 'react';
import { Volume2, Ear, Sliders } from 'lucide-react';

export default function SettingsPanel({
  settings,
  onUpdateSettings,
  onBackToChat,
}) {
  const ttsEnabled = settings?.tts?.enabled ?? true;
  const ttsRate = settings?.tts?.rate ?? 170;
  const wakeWordEnabled = settings?.wake_word?.enabled ?? true;

  const handleToggleTTS = (e) => {
    onUpdateSettings({
      tts: { ...settings.tts, enabled: e.target.checked },
    });
  };

  const handleToggleWakeWord = (e) => {
    onUpdateSettings({
      wake_word: { ...settings.wake_word, enabled: e.target.checked },
    });
  };

  const handleRateChange = (e) => {
    const rate = parseInt(e.target.value, 10);
    onUpdateSettings({
      tts: { ...settings.tts, rate },
    });
  };

  return (
    <div className="settings-panel">
      <div className="settings-header">
        <h3>⚙️ Panel Pengaturan</h3>
      </div>

      <div className="settings-options">
        <label className="setting-card">
          <div className="setting-icon"><Volume2 size={18} /></div>
          <div className="setting-info">
            <span className="setting-title">Membacakan Respon AI (TTS)</span>
            <span className="setting-desc">Mengubah balasan teks menjadi suara</span>
          </div>
          <input
            type="checkbox"
            checked={ttsEnabled}
            onChange={handleToggleTTS}
            className="toggle-checkbox"
          />
        </label>

        <label className="setting-card">
          <div className="setting-icon"><Ear size={18} /></div>
          <div className="setting-info">
            <span className="setting-title">Wake Word (Cat-Themed)</span>
            <span className="setting-desc">"Hi Kitty" / "Mew Mew" / "Hey Kitty"</span>
          </div>
          <input
            type="checkbox"
            checked={wakeWordEnabled}
            onChange={handleToggleWakeWord}
            className="toggle-checkbox"
          />
        </label>

        <div className="setting-card column-card">
          <div className="card-header-row">
            <div className="setting-icon"><Sliders size={18} /></div>
            <div className="setting-info">
              <span className="setting-title">Kecepatan Suara (Rate): {ttsRate}</span>
            </div>
          </div>
          <input
            type="range"
            min="100"
            max="220"
            value={ttsRate}
            onChange={handleRateChange}
            className="range-slider"
          />
        </div>

        <div className="engine-info-card">
          <p><strong>Engine:</strong> openWakeWord (Offline) + Speech Spotter</p>
          <p><strong>AI Brain:</strong> Google Gemini API</p>
          <p><strong>UI Engine:</strong> Tauri v2 + React (Vite)</p>
        </div>
      </div>

      <button className="btn-back" onClick={onBackToChat}>
        🔙 Kembali ke Chat
      </button>
    </div>
  );
}
