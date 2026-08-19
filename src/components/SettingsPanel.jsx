import React, { useState, useEffect } from 'react';
import {
  Volume2,
  Ear,
  Sliders,
  Mic,
  Play,
  ExternalLink,
  Info,
  Globe,
  Palette,
  Sparkles,
  CheckCircle2,
  Bot,
  Key,
  RefreshCw,
  Eye,
  EyeOff,
  Cpu,
  AlertCircle,
} from 'lucide-react';
import {
  fetchAvailableVoices,
  triggerTTS,
  openSpeechSettings,
  openExternalUrl,
  fetchAIProviders,
  testAIConnection,
  fetchOllamaLocalModels,
} from '../services/api';
import { CAT_SKINS, UI_THEMES } from '../config/catRegistry';

export default function SettingsPanel({
  settings,
  onUpdateSettings,
  onBackToChat,
}) {
  const [activeTab, setActiveTab] = useState('ai'); // 'ai' | 'appearance' | 'voice'
  const [voices, setVoices] = useState([]);
  const [isPlayingPreview, setIsPlayingPreview] = useState(false);
  const [showGuide, setShowGuide] = useState(false);

  // AI Multi-Model State
  const [providers, setProviders] = useState([]);
  const [showApiKey, setShowApiKey] = useState(false);
  const [isTestingAi, setIsTestingAi] = useState(false);
  const [aiTestResult, setAiTestResult] = useState(null); // { success: boolean, message: string }
  const [ollamaModels, setOllamaModels] = useState([]);
  const [isLoadingOllama, setIsLoadingOllama] = useState(false);

  const ttsEnabled = settings?.tts?.enabled ?? true;
  const selectedVoiceId = settings?.tts?.voice_id ?? '';
  const wakeWordEnabled = settings?.wake_word?.enabled ?? true;
  const selectedCat = settings?.selected_cat || 'cat_01';
  const selectedTheme = settings?.theme || 'theme-mocha';

  const aiConfig = settings?.ai_provider_config || {
    provider: 'gemini',
    model: 'gemini-1.5-flash',
    temperature: 0.7,
    api_keys: {},
    base_urls: {},
    system_prompt: '',
  };

  const currentProviderId = aiConfig.provider || 'gemini';
  const currentModelId = aiConfig.model || '';
  const currentApiKey = aiConfig.api_keys?.[currentProviderId] || '';
  const currentBaseUrl = aiConfig.base_urls?.[currentProviderId] || '';
  const currentTemperature = aiConfig.temperature ?? 0.7;

  // Local state for debouncing rate & volume sliders
  const [localRate, setLocalRate] = useState(settings?.tts?.rate ?? 160);
  const [localVolume, setLocalVolume] = useState(settings?.tts?.volume ?? 1.0);

  useEffect(() => {
    fetchAvailableVoices().then((voiceList) => {
      if (Array.isArray(voiceList)) {
        setVoices(voiceList);
      }
    });

    fetchAIProviders().then((res) => {
      if (Array.isArray(res)) {
        setProviders(res);
      }
    });
  }, []);

  // Sync local sliders when settings prop arrives
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

  const activeProviderMeta = providers.find((p) => p.id === currentProviderId);

  const handleSelectProvider = (providerId) => {
    const meta = providers.find((p) => p.id === providerId);
    const defaultModel = meta?.default_model || meta?.models?.[0]?.id || '';
    const newAiConfig = {
      ...aiConfig,
      provider: providerId,
      model: defaultModel,
    };
    onUpdateSettings({ ai_provider_config: newAiConfig });
    setAiTestResult(null);

    if (providerId === 'ollama') {
      handleRefreshOllama(newAiConfig.base_urls?.ollama || 'http://localhost:11434');
    }
  };

  const handleSelectModel = (modelId) => {
    const newAiConfig = { ...aiConfig, model: modelId };
    onUpdateSettings({ ai_provider_config: newAiConfig });
    setAiTestResult(null);
  };

  const handleApiKeyChange = (val) => {
    const newKeys = { ...(aiConfig.api_keys || {}), [currentProviderId]: val };
    const newAiConfig = { ...aiConfig, api_keys: newKeys };
    onUpdateSettings({ ai_provider_config: newAiConfig });
  };

  const handleBaseUrlChange = (val) => {
    const newUrls = { ...(aiConfig.base_urls || {}), [currentProviderId]: val };
    const newAiConfig = { ...aiConfig, base_urls: newUrls };
    onUpdateSettings({ ai_provider_config: newAiConfig });
  };

  const handleTemperatureChange = (val) => {
    const newAiConfig = { ...aiConfig, temperature: parseFloat(val) };
    onUpdateSettings({ ai_provider_config: newAiConfig });
  };

  const handleTestAiConnection = async () => {
    setIsTestingAi(true);
    setAiTestResult(null);
    try {
      const res = await testAIConnection(
        currentProviderId,
        currentModelId,
        currentApiKey,
        currentBaseUrl
      );
      if (res.success) {
        setAiTestResult({
          success: true,
          message: `Berhasil! Respon: "${res.response}"`,
        });
      } else {
        setAiTestResult({
          success: false,
          message: `Gagal: ${res.error || 'Tidak dapat terhubung'}`,
        });
      }
    } catch (err) {
      setAiTestResult({
        success: false,
        message: `Error: ${err.message}`,
      });
    } finally {
      setIsTestingAi(false);
    }
  };

  const handleRefreshOllama = async (baseUrl) => {
    setIsLoadingOllama(true);
    const targetUrl = baseUrl || currentBaseUrl || 'http://localhost:11434';
    const models = await fetchOllamaLocalModels(targetUrl);
    setOllamaModels(models);
    setIsLoadingOllama(false);
    if (models.length > 0 && (!currentModelId || !models.some((m) => m.id === currentModelId))) {
      handleSelectModel(models[0].id);
    }
  };

  const handleSelectCatSkin = (catId) => {
    onUpdateSettings({ selected_cat: catId });
  };

  const handleSelectTheme = (themeId) => {
    onUpdateSettings({ theme: themeId });
  };

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
        <h3>⚙️ Pengaturan</h3>
        <div className="settings-tab-switcher">
          <button
            className={`tab-btn ${activeTab === 'ai' ? 'active' : ''}`}
            onClick={() => setActiveTab('ai')}
          >
            <Bot size={13} />
            <span>Model AI</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'appearance' ? 'active' : ''}`}
            onClick={() => setActiveTab('appearance')}
          >
            <Palette size={13} />
            <span>Skin & Tema</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'voice' ? 'active' : ''}`}
            onClick={() => setActiveTab('voice')}
          >
            <Mic size={13} />
            <span>Suara & Mic</span>
          </button>
        </div>
      </div>

      <div className="settings-options scrollable-tab-content">
        {/* ======================================================== */}
        {/* TAB 1: MODEL AI SWITCHER */}
        {/* ======================================================== */}
        {activeTab === 'ai' && (
          <>
            {/* Pilihan Provider AI */}
            <div className="setting-section">
              <div className="section-title">
                <Cpu size={14} />
                <span>Pilih Penyedia AI (Provider)</span>
              </div>
              <div className="provider-grid">
                {providers.map((p) => {
                  const isSelected = currentProviderId === p.id;
                  return (
                    <div
                      key={p.id}
                      className={`provider-card ${isSelected ? 'selected' : ''}`}
                      onClick={() => handleSelectProvider(p.id)}
                    >
                      <div className="provider-header">
                        <span className="provider-name">{p.name}</span>
                        {p.badge && <span className="provider-badge">{p.badge}</span>}
                      </div>
                      <span className="provider-desc">{p.description}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Pilihan Model */}
            <div className="setting-card column-card">
              <div className="card-header-row">
                <div className="setting-icon"><Bot size={18} /></div>
                <div className="setting-info" style={{ flex: 1 }}>
                  <span className="setting-title">Pilih Model AI</span>
                  <span className="setting-desc">{activeProviderMeta?.name || 'Model'}</span>
                </div>
                {currentProviderId === 'ollama' && (
                  <button
                    className="btn-refresh-models"
                    onClick={() => handleRefreshOllama(currentBaseUrl)}
                    disabled={isLoadingOllama}
                    title="Cek model yang terpasang di Ollama"
                  >
                    <RefreshCw size={12} className={isLoadingOllama ? 'spin-icon' : ''} />
                    <span>{isLoadingOllama ? 'Memuat...' : 'Cek Model'}</span>
                  </button>
                )}
              </div>

              {currentProviderId === 'custom' ? (
                <input
                  type="text"
                  value={currentModelId}
                  onChange={(e) => handleSelectModel(e.target.value)}
                  placeholder="Nama model kustom (contoh: llama-3-8b)"
                  className="settings-text-input"
                />
              ) : (
                <select
                  value={currentModelId}
                  onChange={(e) => handleSelectModel(e.target.value)}
                  className="voice-select"
                >
                  {(currentProviderId === 'ollama' && ollamaModels.length > 0
                    ? ollamaModels
                    : activeProviderMeta?.models || []
                  ).map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name || m.id}
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* Base URL (Untuk Ollama & Custom Endpoint) */}
            {(currentProviderId === 'ollama' || currentProviderId === 'custom') && (
              <div className="setting-card column-card">
                <div className="card-header-row">
                  <div className="setting-icon"><Globe size={18} /></div>
                  <div className="setting-info">
                    <span className="setting-title">Endpoint Base URL</span>
                  </div>
                </div>
                <input
                  type="text"
                  value={currentBaseUrl || (currentProviderId === 'ollama' ? 'http://localhost:11434/v1' : 'http://localhost:1234/v1')}
                  onChange={(e) => handleBaseUrlChange(e.target.value)}
                  placeholder="http://localhost:11434/v1"
                  className="settings-text-input"
                />
              </div>
            )}

            {/* Input API Key */}
            {currentProviderId !== 'ollama' && (
              <div className="setting-card column-card">
                <div className="card-header-row">
                  <div className="setting-icon"><Key size={18} /></div>
                  <div className="setting-info" style={{ flex: 1 }}>
                    <span className="setting-title">
                      {currentProviderId === 'custom'
                        ? 'API Key (Kustom / Cloud)'
                        : `API Key ${activeProviderMeta?.name || ''}`}
                    </span>
                    <span className="setting-desc">
                      {currentProviderId === 'custom'
                        ? 'Opsional untuk server lokal, wajib untuk cloud provider'
                        : 'Tersimpan aman secara lokal'}
                    </span>
                  </div>
                  {activeProviderMeta?.doc_url && (
                    <button
                      className="btn-get-key"
                      onClick={() => openExternalUrl(activeProviderMeta.doc_url)}
                      title="Dapatkan API Key di Web Resmi"
                    >
                      <ExternalLink size={12} />
                      <span>Dapatkan Key</span>
                    </button>
                  )}
                </div>
                <div className="api-key-input-wrapper">
                  <input
                    type={showApiKey ? 'text' : 'password'}
                    value={currentApiKey}
                    onChange={(e) => handleApiKeyChange(e.target.value)}
                    placeholder={
                      currentProviderId === 'custom'
                        ? 'Masukkan API Key jika diperlukan (misal: sk-or-...)...'
                        : `Masukkan ${activeProviderMeta?.name || 'API'} Key...`
                    }
                    className="settings-text-input key-input"
                  />
                  <button
                    className="btn-toggle-show-key"
                    onClick={() => setShowApiKey(!showApiKey)}
                    title={showApiKey ? 'Sembunyikan' : 'Tampilkan'}
                  >
                    {showApiKey ? <EyeOff size={14} /> : <Eye size={14} />}
                  </button>
                </div>
              </div>
            )}

            {/* Slider Temperature (Kreativitas) */}
            <div className="setting-card column-card">
              <div className="card-header-row">
                <div className="setting-icon"><Sliders size={18} /></div>
                <div className="setting-info">
                  <span className="setting-title">
                    Tingkat Kreativitas (Temperature): {currentTemperature}
                  </span>
                  <span className="setting-desc">
                    {currentTemperature < 0.4 ? 'Faktual & Presisi' : currentTemperature > 0.8 ? 'Sangat Kreatif & Variatif' : 'Seimbang & Alami'}
                  </span>
                </div>
              </div>
              <input
                type="range"
                min="0.0"
                max="1.0"
                step="0.05"
                value={currentTemperature}
                onChange={(e) => handleTemperatureChange(e.target.value)}
                className="range-slider"
              />
            </div>

            {/* Tombol Tes Koneksi AI */}
            <div className="ai-test-container">
              <button
                className="btn-test-ai"
                onClick={handleTestAiConnection}
                disabled={isTestingAi}
              >
                <Sparkles size={14} className={isTestingAi ? 'spin-icon' : ''} />
                <span>{isTestingAi ? 'Menguji Koneksi...' : '⚡ Tes Koneksi Model AI'}</span>
              </button>

              {aiTestResult && (
                <div className={`ai-test-badge ${aiTestResult.success ? 'success' : 'error'}`}>
                  {aiTestResult.success ? <CheckCircle2 size={14} /> : <AlertCircle size={14} />}
                  <span>{aiTestResult.message}</span>
                </div>
              )}
            </div>
          </>
        )}

        {/* ======================================================== */}
        {/* TAB 2: APPEARANCE & SKIN */}
        {/* ======================================================== */}
        {activeTab === 'appearance' && (
          <>
            {/* Skin Kucing */}
            <div className="setting-section">
              <div className="section-title">
                <Sparkles size={14} />
                <span>Pilih Karakter Kucing</span>
              </div>
              <div className="skin-grid">
                {Object.values(CAT_SKINS).map((cat) => {
                  const isSelected = selectedCat === cat.id;
                  return (
                    <div
                      key={cat.id}
                      className={`skin-card ${isSelected ? 'selected' : ''}`}
                      onClick={() => handleSelectCatSkin(cat.id)}
                    >
                      <div className="skin-preview-wrapper">
                        <img src={cat.preview} alt={cat.name} className="skin-preview-img" />
                        {isSelected && (
                          <div className="skin-check-badge">
                            <CheckCircle2 size={16} />
                          </div>
                        )}
                      </div>
                      <div className="skin-details">
                        <span className="skin-name">{cat.name}</span>
                        <span className="skin-desc">{cat.description}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Tema UI */}
            <div className="setting-section">
              <div className="section-title">
                <Palette size={14} />
                <span>Tema Warna Tampilan</span>
              </div>
              <div className="theme-list">
                {UI_THEMES.map((th) => {
                  const isSelected = selectedTheme === th.id;
                  return (
                    <div
                      key={th.id}
                      className={`theme-item ${isSelected ? 'selected' : ''}`}
                      onClick={() => handleSelectTheme(th.id)}
                    >
                      <div className="theme-color-dot" style={{ backgroundColor: th.badgeColor }}></div>
                      <div className="theme-info">
                        <span className="theme-title">{th.name}</span>
                        <span className="theme-desc">{th.description}</span>
                      </div>
                      {isSelected && <CheckCircle2 size={16} className="theme-check-icon" />}
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        )}

        {/* ======================================================== */}
        {/* TAB 3: VOICE & MIC */}
        {/* ======================================================== */}
        {activeTab === 'voice' && (
          <>
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

            {/* Shortcut & Guide Paket Suara Windows */}
            <div className="voice-pack-card">
              <div className="voice-pack-header">
                <Info size={14} className="info-icon" />
                <span className="voice-pack-title">Panduan Unduh Paket Suara (Voice Packs)</span>
              </div>
              <p className="voice-pack-desc">
                Ingin suara Bahasa Indonesia atau bahasa lainnya? Gunakan tombol di bawah ini.
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
                  <span>Panduan Suara (Browser)</span>
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
                    <li>Setelah selesai, suara baru otomatis muncul di pilihan suara di atas!</li>
                  </ol>
                </div>
              )}
            </div>
          </>
        )}
      </div>

      <button className="btn-back" onClick={onBackToChat}>
        🔙 Kembali ke Chat
      </button>
    </div>
  );
}
