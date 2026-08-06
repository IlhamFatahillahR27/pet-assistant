import React, { useState, useEffect } from 'react';
import { Volume2, Ear, Sliders, Mic, Play, ExternalLink, Info, Globe } from 'lucide-react';
import { fetchAvailableVoices, triggerTTS, openSpeechSettings, openExternalUrl } from '../services/api';

export default function SettingsPanel({
  settings,
  onUpdateSettings,
  onBackToChat,
}) {
  const [voices, setVoices] = useState([]);
  const [isPlayingPreview, setIsPlayingPreview] = useState(false);
  const [showGuide, setShowGuide] = useState(false);

  const ttsEnabled = settings?.tts?.enabled ?? true;
  const selectedVoiceId = settings?.tts?.voice_id ?? '';
  const wakeWordEnabled = settings?.wake_word?.enabled ?? true;

  // Local state for debouncing rate & volume sliders
  const [localRate, setLocalRate] = useState(settings?.tts?.rate ?? 160);
  const [localVolume, setLocalVolume] = useState(settings?.tts?.volume ?? 1.0);

  useEffect(() => {
    fetchAvailableVoices().then((voiceList) => {
      if (Array.isArray(voiceList)) {
        setVoices(voiceList);
      }
    });
  }, []);

  // Sync local sliders when settings prop arrives from initial fetch
  useEffect(() => {
    if (settings?.tts?.rate !== undefined) setLocalRate(settings.tts.rate);
    if (settings?.tts?.volume !== undefined) setLocalVolume(settings.tts.volume);
  }, [settings?.tts?.rate, settings?.tts?.volume]);

  // Debounce API calls for rate & volume sliders (400ms delay)
  useEffect(() => {
    const handler = setTimeout(() => {
      if (
        settings?.tts &&
        (localRate !== settings.tts.rate || localVolume !== settings.tts.volume)
      ) {
        onUpdateSettings({
          tts: { ...settings.tts, rate: localRate, volume: localVolume },
        });
      }
    }, 400);

    return () => clearTimeout(handler);
  }, [localRate, localVolume]);

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

  const handleVoiceChange = (e) => {
    const voice_id = e.target.value;
    onUpdateSettings({
      tts: { ...settings.tts, voice_id },
    });
  };

  const handlePreviewVoice = async () => {
    setIsPlayingPreview(true);
    const sampleText = 'Halo Nyaa~! Ini adalah contoh sampel suara Kitty yang kamu pilih.';
    await triggerTTS(sampleText, localRate, localVolume, selectedVoiceId);
    setTimeout(() => setIsPlayingPreview(false), 2500);
  };

  const handleOpenSpeechSettings = async () => {
    await openSpeechSettings();
  };

  const handleOpenOfficialGuide = async () => {
    const guideUrl = 'https://support.microsoft.com/en-us/windows/appendix-a-supported-languages-and-voices-2548d543-5ced-43e7-9c01-76b66ef52c61';
    await openExternalUrl(guideUrl);
  };

  return (
    <div className="settings-panel">
      <div className="settings-header">
        <h3>⚙️ Panel Pengaturan Asisten</h3>
      </div>

      <div className="settings-options">
        {/* Toggle TTS */}
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

        {/* Voice Selector & Preview */}
        {ttsEnabled && (
          <div className="setting-card column-card">
            <div className="card-header-row">
              <div className="setting-icon"><Mic size={18} /></div>
              <div className="setting-info" style={{ flex: 1 }}>
                <span className="setting-title">Pilihan Suara Asisten (Voice ID)</span>
                <span className="setting-desc">Pilih suara SAPI5 / Windows OneCore</span>
              </div>
              <button
                className="btn-preview-voice"
                onClick={handlePreviewVoice}
                disabled={isPlayingPreview}
                title="Dengarkan Contoh Suara"
              >
                <Play size={12} />
                <span>{isPlayingPreview ? 'Memutar...' : 'Tes Suara'}</span>
              </button>
            </div>
            <select
              value={selectedVoiceId}
              onChange={handleVoiceChange}
              className="voice-select"
            >
              <option value="">-- Otomatis Berdasarkan Bahasa (Default) --</option>
              {voices.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Kecepatan Suara (Rate) dengan Debounce */}
        {ttsEnabled && (
          <div className="setting-card column-card">
            <div className="card-header-row">
              <div className="setting-icon"><Sliders size={18} /></div>
              <div className="setting-info">
                <span className="setting-title">Kecepatan Suara (Rate): {localRate}</span>
              </div>
            </div>
            <input
              type="range"
              min="100"
              max="240"
              step="5"
              value={localRate}
              onChange={(e) => setLocalRate(parseInt(e.target.value, 10))}
              className="range-slider"
            />
          </div>
        )}

        {/* Volume Suara dengan Debounce */}
        {ttsEnabled && (
          <div className="setting-card column-card">
            <div className="card-header-row">
              <div className="setting-icon"><Volume2 size={18} /></div>
              <div className="setting-info">
                <span className="setting-title">Volume Suara: {Math.round(localVolume * 100)}%</span>
              </div>
            </div>
            <input
              type="range"
              min="0.1"
              max="1.0"
              step="0.05"
              value={localVolume}
              onChange={(e) => setLocalVolume(parseFloat(e.target.value))}
              className="range-slider"
            />
          </div>
        )}

        {/* Toggle Wake Word */}
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

        {/* Shortcut & Guide Paket Suara Windows dengan Link Browser */}
        <div className="voice-pack-card">
          <div className="voice-pack-header">
            <Info size={14} className="info-icon" />
            <span className="voice-pack-title">Panduan Unduh Paket Suara (Voice Packs)</span>
          </div>
          <p className="voice-pack-desc">
            Ingin suara Bahasa Indonesia (seperti Microsoft Gadis/Andika) atau bahasa lainnya? Gunakan tombol di bawah ini.
          </p>

          <div className="voice-pack-actions">
            <button
              className="btn-open-speech-settings"
              onClick={handleOpenSpeechSettings}
              title="Buka Pengaturan Suara Windows"
            >
              <ExternalLink size={12} />
              <span>Buka Settings Windows</span>
            </button>

            <button
              className="btn-open-browser-guide"
              onClick={handleOpenOfficialGuide}
              title="Buka Web Resmi Dokumentasi Paket Suara Microsoft di Browser"
            >
              <Globe size={12} />
              <span>Panduan Suara Microsoft (Browser)</span>
            </button>
          </div>

          <button
            className="btn-toggle-guide"
            onClick={() => setShowGuide(!showGuide)}
          >
            {showGuide ? '▲ Sembunyikan Petunjuk' : '▼ Lihat Cara Install Voice Pack Windows'}
          </button>

          {showGuide && (
            <div className="guide-steps">
              <ol>
                <li>Klik tombol <strong>"Buka Settings Windows"</strong> di atas.</li>
                <li>Pada menu Windows Speech Settings, klik <strong>"Add voices"</strong>.</li>
                <li>Cari paket suara yang diinginkan (contoh: <strong>Indonesian</strong> atau <strong>Japanese</strong>).</li>
                <li>Centang dan klik <strong>Add</strong> untuk mengunduh.</li>
                <li>Setelah selesai, suara baru otomatis muncul di dropdown pilihan suara di atas!</li>
              </ol>
            </div>
          )}
        </div>
      </div>

      <button className="btn-back" onClick={onBackToChat}>
        🔙 Kembali ke Chat
      </button>
    </div>
  );
}
