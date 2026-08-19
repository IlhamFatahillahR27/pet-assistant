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
  Calendar,
  CheckSquare,
  Mail,
  Plus,
  Trash2,
  LogOut,
  User,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import {
  fetchAvailableVoices,
  triggerTTS,
  openSpeechSettings,
  openExternalUrl,
  fetchAIProviders,
  testAIConnection,
  fetchOllamaLocalModels,
  fetchGoogleStatus,
  getGoogleAuthUrl,
  logoutGoogle,
  saveGoogleConfig,
  fetchCalendarEvents,
  createCalendarEvent,
  deleteCalendarEvent,
  fetchGoogleTasks,
  createGoogleTask,
  completeGoogleTask,
  deleteGoogleTask,
  fetchUnreadEmails,
} from '../services/api';
import { CAT_SKINS, UI_THEMES } from '../config/catRegistry';

export default function SettingsPanel({
  settings,
  onUpdateSettings,
  onBackToChat,
}) {
  const [activeTab, setActiveTab] = useState('ai'); // 'ai' | 'google' | 'appearance' | 'voice'
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

  // Google OAuth & Workspace State
  const [googleStatus, setGoogleStatus] = useState({
    connected: false,
    configured: false,
    user: null,
    scopes: [],
  });
  const [calendarEvents, setCalendarEvents] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [unreadEmails, setUnreadEmails] = useState([]);
  const [isLoadingGoogle, setIsLoadingGoogle] = useState(false);
  const [showOAuthConfig, setShowOAuthConfig] = useState(false);
  const [customClientId, setCustomClientId] = useState(settings?.google_oauth?.client_id || '');
  const [customClientSecret, setCustomClientSecret] = useState(settings?.google_oauth?.client_secret || '');
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newEventSummary, setNewEventSummary] = useState('');
  const [newEventStart, setNewEventStart] = useState('');
  const [showAddEvent, setShowAddEvent] = useState(false);

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

    loadGoogleStatus();
  }, []);

  const loadGoogleStatus = async () => {
    const status = await fetchGoogleStatus();
    setGoogleStatus(status);
    if (status?.connected) {
      loadGoogleWorkspaceData();
    }
  };

  const loadGoogleWorkspaceData = async () => {
    setIsLoadingGoogle(true);
    try {
      const [events, taskList, emails] = await Promise.all([
        fetchCalendarEvents(5, 7),
        fetchGoogleTasks(false, 10),
        fetchUnreadEmails(5),
      ]);
      setCalendarEvents(events);
      setTasks(taskList);
      setUnreadEmails(emails);
    } catch (err) {
      console.error('Error loading Google Workspace data:', err);
    } finally {
      setIsLoadingGoogle(false);
    }
  };

  const handleConnectGoogle = async () => {
    const res = await getGoogleAuthUrl();
    if (res?.success && res?.auth_url) {
      await openExternalUrl(res.auth_url);
    } else {
      alert(res?.error || 'Gagal membuat URL login Google. Pastikan Client ID sudah dikonfigurasi.');
    }
  };

  const handleLogoutGoogle = async () => {
    if (window.confirm('Yakin ingin memutuskan koneksi akun Google?')) {
      await logoutGoogle();
      setGoogleStatus({ connected: false, configured: false, user: null, scopes: [] });
      setCalendarEvents([]);
      setTasks([]);
      setUnreadEmails([]);
    }
  };

  const handleSaveOAuthConfig = async (e) => {
    e.preventDefault();
    const res = await saveGoogleConfig(customClientId, customClientSecret);
    if (res?.status === 'success') {
      alert('Kredensial Google OAuth berhasil disimpan!');
      if (res.auth_status) setGoogleStatus(res.auth_status);
      setShowOAuthConfig(false);
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;
    const res = await createGoogleTask(newTaskTitle.trim());
    if (res?.success) {
      setNewTaskTitle('');
      const updated = await fetchGoogleTasks(false, 10);
      setTasks(updated);
    }
  };

  const handleCompleteTask = async (taskId) => {
    await completeGoogleTask(taskId);
    setTasks((prev) => prev.filter((t) => t.id !== taskId));
  };

  const handleDeleteTask = async (taskId) => {
    await deleteGoogleTask(taskId);
    setTasks((prev) => prev.filter((t) => t.id !== taskId));
  };

  const handleCreateCalendarEvent = async (e) => {
    e.preventDefault();
    if (!newEventSummary.trim() || !newEventStart) return;
    const res = await createCalendarEvent(newEventSummary.trim(), newEventStart);
    if (res?.success) {
      setNewEventSummary('');
      setNewEventStart('');
      setShowAddEvent(false);
      const updated = await fetchCalendarEvents(5, 7);
      setCalendarEvents(updated);
    }
  };

  const handleDeleteCalendarEvent = async (eventId) => {
    await deleteCalendarEvent(eventId);
    setCalendarEvents((prev) => prev.filter((ev) => ev.id !== eventId));
  };

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
            className={`tab-btn ${activeTab === 'google' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('google');
              loadGoogleStatus();
            }}
          >
            <Globe size={13} />
            <span>Google Hub</span>
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

        {/* ======================================================== */}
        {/* TAB 4: GOOGLE OAUTH & WORKSPACE HUB */}
        {/* ======================================================== */}
        {activeTab === 'google' && (
          <>
            {/* Status Akun Google */}
            <div className="google-account-card">
              {googleStatus.connected && googleStatus.user ? (
                <div className="google-profile-connected">
                  <div className="google-avatar-wrapper">
                    {googleStatus.user.picture ? (
                      <img src={googleStatus.user.picture} alt="Avatar" className="google-avatar-img" />
                    ) : (
                      <div className="google-avatar-fallback"><User size={18} /></div>
                    )}
                    <span className="google-online-dot"></span>
                  </div>
                  <div className="google-user-details">
                    <span className="google-user-name">{googleStatus.user.name}</span>
                    <span className="google-user-email">{googleStatus.user.email}</span>
                    <span className="google-connected-badge">🟢 Terhubung ke Google</span>
                  </div>
                  <button
                    className="btn-google-logout"
                    onClick={handleLogoutGoogle}
                    title="Putuskan Hubungan Akun Google"
                  >
                    <LogOut size={12} />
                    <span>Putuskan</span>
                  </button>
                </div>
              ) : (
                <div className="google-profile-disconnected">
                  <div className="google-promo-header">
                    <div className="google-promo-icon-box">
                      <Globe size={20} className="google-promo-icon" />
                    </div>
                    <div className="google-promo-texts">
                      <span className="google-promo-title">Hubungkan Akun Google</span>
                      <p className="google-promo-desc">
                        Akses Google Calendar, Tasks, dan Gmail langsung melalui Kitty!
                      </p>
                    </div>
                  </div>
                  <button
                    className="btn-google-login"
                    onClick={handleConnectGoogle}
                  >
                    <Globe size={13} />
                    <span>🔗 Login & Hubungkan Akun Google</span>
                  </button>
                </div>
              )}
            </div>

            {/* Google Workspace Live Hub (Ketika Terhubung) */}
            {googleStatus.connected && (
              <>
                {/* 📅 Google Calendar Section */}
                <div className="workspace-card">
                  <div className="workspace-card-header">
                    <div className="workspace-title-row">
                      <Calendar size={14} className="workspace-icon cal-color" />
                      <span className="workspace-title">Agenda Kalender (7 Hari)</span>
                    </div>
                    <div className="workspace-actions">
                      <button
                        className="btn-workspace-action"
                        onClick={() => setShowAddEvent(!showAddEvent)}
                        title="Tambah Agenda Baru"
                      >
                        <Plus size={11} />
                        <span>Agenda</span>
                      </button>
                      <button
                        className="btn-workspace-action"
                        onClick={loadGoogleWorkspaceData}
                        disabled={isLoadingGoogle}
                        title="Segarkan Data"
                      >
                        <RefreshCw size={11} className={isLoadingGoogle ? 'spin-icon' : ''} />
                      </button>
                    </div>
                  </div>

                  {showAddEvent && (
                    <form onSubmit={handleCreateCalendarEvent} className="workspace-add-form">
                      <input
                        type="text"
                        placeholder="Nama kegiatan (contoh: Rapat Tim)"
                        value={newEventSummary}
                        onChange={(e) => setNewEventSummary(e.target.value)}
                        className="settings-text-input"
                        required
                      />
                      <input
                        type="datetime-local"
                        value={newEventStart}
                        onChange={(e) => setNewEventStart(e.target.value)}
                        className="settings-text-input"
                        required
                      />
                      <div className="form-buttons-row">
                        <button type="submit" className="btn-form-submit">Simpan ke Kalender</button>
                        <button type="button" className="btn-form-cancel" onClick={() => setShowAddEvent(false)}>Batal</button>
                      </div>
                    </form>
                  )}

                  <div className="workspace-item-list">
                    {calendarEvents.length === 0 ? (
                      <span className="workspace-empty">Tidak ada agenda mendatang.</span>
                    ) : (
                      calendarEvents.map((ev) => (
                        <div key={ev.id} className="workspace-item calendar-item">
                          <div className="item-content">
                            <span className="item-title">{ev.summary}</span>
                            <span className="item-sub">
                              🕒 {new Date(ev.start).toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' })}
                              {ev.location && ` • 📍 ${ev.location}`}
                            </span>
                          </div>
                          <button
                            className="btn-item-delete"
                            onClick={() => handleDeleteCalendarEvent(ev.id)}
                            title="Hapus Agenda"
                          >
                            <Trash2 size={11} />
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* ✅ Google Tasks Section */}
                <div className="workspace-card">
                  <div className="workspace-card-header">
                    <div className="workspace-title-row">
                      <CheckSquare size={14} className="workspace-icon task-color" />
                      <span className="workspace-title">Daftar Tugas (Google Tasks)</span>
                    </div>
                    <button
                      className="btn-workspace-action"
                      onClick={loadGoogleWorkspaceData}
                      disabled={isLoadingGoogle}
                      title="Segarkan Data"
                    >
                      <RefreshCw size={11} className={isLoadingGoogle ? 'spin-icon' : ''} />
                    </button>
                  </div>

                  <form onSubmit={handleCreateTask} className="workspace-quick-add">
                    <input
                      type="text"
                      placeholder="Tulis tugas baru..."
                      value={newTaskTitle}
                      onChange={(e) => setNewTaskTitle(e.target.value)}
                      className="settings-text-input"
                    />
                    <button type="submit" className="btn-quick-add" disabled={!newTaskTitle.trim()}>
                      <Plus size={13} />
                    </button>
                  </form>

                  <div className="workspace-item-list">
                    {tasks.length === 0 ? (
                      <span className="workspace-empty">Tidak ada tugas aktif (Semua selesai!).</span>
                    ) : (
                      tasks.map((t) => (
                        <div key={t.id} className="workspace-item task-item">
                          <input
                            type="checkbox"
                            checked={t.status === 'completed'}
                            onChange={() => handleCompleteTask(t.id)}
                            className="task-checkbox"
                            title="Tandai Selesai"
                          />
                          <span className="task-title-text">{t.title}</span>
                          <button
                            className="btn-item-delete"
                            onClick={() => handleDeleteTask(t.id)}
                            title="Hapus Tugas"
                          >
                            <Trash2 size={11} />
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* ✉️ Gmail Unread Section */}
                <div className="workspace-card">
                  <div className="workspace-card-header">
                    <div className="workspace-title-row">
                      <Mail size={14} className="workspace-icon mail-color" />
                      <span className="workspace-title">Email Belum Dibaca (Inbox)</span>
                    </div>
                    <button
                      className="btn-workspace-action"
                      onClick={loadGoogleWorkspaceData}
                      disabled={isLoadingGoogle}
                      title="Segarkan Data"
                    >
                      <RefreshCw size={11} className={isLoadingGoogle ? 'spin-icon' : ''} />
                    </button>
                  </div>

                  <div className="workspace-item-list">
                    {unreadEmails.length === 0 ? (
                      <span className="workspace-empty">Kotak masuk bersih! Tidak ada email unread.</span>
                    ) : (
                      unreadEmails.map((m) => (
                        <div key={m.id} className="workspace-item email-item">
                          <div className="email-header-row">
                            <span className="email-from">{m.from.split('<')[0]}</span>
                            <span className="email-date">{m.date ? new Date(m.date).toLocaleDateString('id-ID') : ''}</span>
                          </div>
                          <span className="email-subject">{m.subject}</span>
                          <span className="email-snippet">{m.snippet}</span>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </>
            )}

            {/* ⚙️ Form Kredensial OAuth Kustom */}
            <div className="oauth-config-accordion">
              <button
                className="btn-toggle-oauth-config"
                onClick={() => setShowOAuthConfig(!showOAuthConfig)}
              >
                <Key size={12} />
                <span>Kredensial OAuth Google Cloud (Opsional)</span>
                {showOAuthConfig ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
              </button>

              {showOAuthConfig && (
                <form onSubmit={handleSaveOAuthConfig} className="oauth-config-form">
                  <span className="oauth-config-guide">
                    Masukkan Client ID & Secret dari <strong>Google Cloud Console</strong> untuk menghubungkan akun Google Anda sendiri:
                  </span>
                  <div className="input-group">
                    <label className="input-label">Client ID:</label>
                    <input
                      type="text"
                      placeholder="xxxx.apps.googleusercontent.com"
                      value={customClientId}
                      onChange={(e) => setCustomClientId(e.target.value)}
                      className="settings-text-input"
                      required
                    />
                  </div>
                  <div className="input-group">
                    <label className="input-label">Client Secret:</label>
                    <input
                      type="password"
                      placeholder="GOCSPX-..."
                      value={customClientSecret}
                      onChange={(e) => setCustomClientSecret(e.target.value)}
                      className="settings-text-input"
                      required
                    />
                  </div>
                  <button type="submit" className="btn-save-oauth">
                    Simpan Kredensial Google
                  </button>
                </form>
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
