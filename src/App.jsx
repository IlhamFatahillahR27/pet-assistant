import React, { useState, useEffect, useRef, useCallback } from 'react';
import Header from './components/Header';
import PetWidget from './components/PetWidget';
import ChatPanel from './components/ChatPanel';
import SettingsPanel from './components/SettingsPanel';
import MemoryPanel from './components/MemoryPanel';
import { wsClient } from './services/websocket';
import {
  fetchSettings,
  updateSettings,
  sendChatMessage,
  triggerSTT,
  fetchMemories,
  addMemory,
  deleteMemory,
  clearMemories,
} from './services/api';
import { getCurrentWindow, LogicalPosition, currentMonitor } from '@tauri-apps/api/window';
import { listen } from '@tauri-apps/api/event';

export default function App() {
  const [currentView, setCurrentView] = useState('chat'); // 'chat', 'memory', 'settings'
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [messages, setMessages] = useState([]);
  const [memories, setMemories] = useState([]);
  const [statusText, setStatusText] = useState('Status: Idle');
  const [isMicActive, setIsMicActive] = useState(false);
  const [isAiThinking, setIsAiThinking] = useState(false);
  const [isAiSpeaking, setIsAiSpeaking] = useState(false);
  const [isAfkSleeping, setIsAfkSleeping] = useState(false);
  const [isWindowMoving, setIsWindowMoving] = useState(false);
  const [settings, setSettings] = useState({
    selected_cat: 'cat_01',
    theme: 'theme-mocha',
    tts: { enabled: true, rate: 160, volume: 1.0 },
    wake_word: { enabled: true },
  });

  const afkTimerRef = useRef(null);
  const moveTimerRef = useRef(null);

  // Inactivity timeout handler (45 seconds of idle triggers sleeping pose)
  const resetAfkTimer = useCallback(() => {
    setIsAfkSleeping(false);
    if (afkTimerRef.current) clearTimeout(afkTimerRef.current);
    afkTimerRef.current = setTimeout(() => {
      setIsAfkSleeping(true);
    }, 45000);
  }, []);

  useEffect(() => {
    // Reset timer on user interactions
    const handleUserActivity = () => resetAfkTimer();
    window.addEventListener('mousemove', handleUserActivity);
    window.addEventListener('keydown', handleUserActivity);
    window.addEventListener('click', handleUserActivity);

    resetAfkTimer();

    return () => {
      if (afkTimerRef.current) clearTimeout(afkTimerRef.current);
      window.removeEventListener('mousemove', handleUserActivity);
      window.removeEventListener('keydown', handleUserActivity);
      window.removeEventListener('click', handleUserActivity);
    };
  }, [resetAfkTimer]);

  useEffect(() => {
    let unlistenMoved = null;
    let unlistenCustomMove = null;
    let isMounted = true;
    let isInitialized = false;

    const handleMovementTrigger = () => {
      if (!isMounted || !isInitialized) return;
      setIsWindowMoving(true);
      resetAfkTimer();

      if (moveTimerRef.current) clearTimeout(moveTimerRef.current);
      moveTimerRef.current = setTimeout(() => {
        if (isMounted) setIsWindowMoving(false);
      }, 350);
    };

    // 0. Set initial position at bottom-right, then activate move listeners
    const initPositionAndListeners = async () => {
      try {
        const appWindow = getCurrentWindow();
        const monitor = await currentMonitor();
        if (monitor) {
          const screenWidth = monitor.size.width / monitor.scaleFactor;
          const screenHeight = monitor.size.height / monitor.scaleFactor;
          const winWidth = 500;
          const winHeight = 420;
          const margin = 20;
          const taskbarOffset = 40;

          const x = Math.max(0, screenWidth - winWidth - margin);
          const y = Math.max(0, screenHeight - winHeight - margin - taskbarOffset);

          await appWindow.setPosition(new LogicalPosition(x, y));
        }
      } catch (err) {
        console.warn('Tauri window positioning notice:', err);
      }

      // Allow 500ms for OS position to settle before listening for user dragging
      setTimeout(async () => {
        if (!isMounted) return;
        isInitialized = true;
        setIsWindowMoving(false);
        try {
          const appWindow = getCurrentWindow();
          unlistenMoved = await appWindow.onMoved(handleMovementTrigger);
          unlistenCustomMove = await listen('window-moving', handleMovementTrigger);
        } catch (err) {
          console.warn('Tauri move event listener notice:', err);
        }
      }, 500);
    };

    initPositionAndListeners();

    // 1. Fetch initial settings & memories
    fetchSettings().then((res) => {
      if (res && isMounted) setSettings((prev) => ({ ...prev, ...res }));
    });

    fetchMemories().then((mems) => {
      if (mems && isMounted) setMemories(mems);
    });

    // 2. Connect WebSocket
    wsClient.connect();

    // 3. Register WebSocket Event Listeners
    const unsubConnected = wsClient.on('connected', (data) => {
      setStatusText('Status: Terhubung');
      if (data?.memories) {
        setMemories(data.memories);
      }
    });

    const unsubDisconnected = wsClient.on('disconnected', () => {
      setStatusText('Status: Terputus');
    });

    const unsubWakeword = wsClient.on('wakeword_detected', (data) => {
      console.log('[App] Wake word terdeteksi:', data);
      setIsMicActive(true);
      setIsAiThinking(false);
      setIsAiSpeaking(false);
      resetAfkTimer();
      setStatusText(`🎙️ Kata Pemicu '${data.model}' Terdeteksi!`);
      triggerSTT();
    });

    const unsubSTTStatus = wsClient.on('stt_status', (data) => {
      resetAfkTimer();
      if (data.status === 'listening') {
        setIsMicActive(true);
        setIsAiThinking(false);
        setIsAiSpeaking(false);
        setStatusText('🎙️ Silakan Berbicara...');
      } else if (data.status === 'processing') {
        setIsMicActive(false);
        setIsAiThinking(true);
        setIsAiSpeaking(false);
        setStatusText('🤖 Memproses Suara...');
      } else if (data.status === 'recognized') {
        setIsMicActive(false);
        setIsAiThinking(true);
        setMessages((prev) => [...prev, { sender: 'Anda', text: data.text }]);
        setStatusText('🤖 Berpikir...');
      } else if (data.status === 'error') {
        setIsMicActive(false);
        setIsAiThinking(false);
        setIsAiSpeaking(false);
        setStatusText(`Status: Error (${data.error})`);
      }
    });

    const unsubChatChunk = wsClient.on('chat_chunk', (data) => {
      resetAfkTimer();
      if (data.done) {
        if (data.full_text) {
          setMessages((prev) => {
            const filtered = prev.filter((m) => !m.isStreaming);
            return [...filtered, { sender: 'Asisten', text: data.full_text }];
          });
        }
        setStatusText('Status: Idle');
        setIsMicActive(false);
        setIsAiThinking(false);
        // Biarkan pose licking aktif sejenak setelah selesai bicara
        setTimeout(() => setIsAiSpeaking(false), 2000);
      } else if (data.text) {
        setStatusText('🤖 Menjawab...');
        setIsAiThinking(false);
        setIsAiSpeaking(true);
        setMessages((prev) => {
          const lastIndex = prev.length - 1;
          if (lastIndex >= 0 && prev[lastIndex].sender === 'Asisten' && prev[lastIndex].isStreaming) {
            const updated = [...prev];
            updated[lastIndex] = {
              ...updated[lastIndex],
              text: updated[lastIndex].text + data.text,
            };
            return updated;
          } else {
            return [...prev, { sender: 'Asisten', text: data.text, isStreaming: true }];
          }
        });
      }
    });

    const unsubMemoryUpdated = wsClient.on('memory_updated', (updatedMemories) => {
      console.log('[App] Memory updated from backend:', updatedMemories);
      if (Array.isArray(updatedMemories)) {
        setMemories(updatedMemories);
      }
    });

    const unsubGoogleAuth = wsClient.on('google_auth_changed', (authStatus) => {
      console.log('[App] Google auth changed:', authStatus);
      if (authStatus?.connected && authStatus?.user) {
        setStatusText(`✨ Google Terhubung: ${authStatus.user.name}`);
      }
    });

    return () => {
      isMounted = false;
      if (typeof unlistenMoved === 'function') {
        unlistenMoved();
      }
      if (moveTimerRef.current) {
        clearTimeout(moveTimerRef.current);
      }
      unsubConnected();
      unsubDisconnected();
      unsubWakeword();
      unsubSTTStatus();
      unsubChatChunk();
      unsubMemoryUpdated();
      unsubGoogleAuth();
    };
  }, [resetAfkTimer]);

  const handleSendMessage = async (text) => {
    resetAfkTimer();
    setMessages((prev) => [...prev, { sender: 'Anda', text }]);
    setStatusText('🤖 Berpikir...');
    setIsAiThinking(true);
    setIsAiSpeaking(false);

    // Kirim via WebSocket jika terhubung, fallback ke REST
    if (wsClient.isConnected) {
      wsClient.send('chat', { prompt: text });
    } else {
      const res = await sendChatMessage(text);
      setIsAiThinking(false);
      if (res && res.response) {
        setIsAiSpeaking(true);
        setMessages((prev) => [...prev, { sender: 'Asisten', text: res.response }]);
        setStatusText('Status: Idle');
        setTimeout(() => setIsAiSpeaking(false), 2000);
      } else {
        setStatusText('Status: Error mengirim pesan');
      }
    }
  };

  const handleStartMic = async () => {
    resetAfkTimer();
    setIsMicActive(true);
    setIsAiThinking(false);
    setIsAiSpeaking(false);
    setStatusText('🎙️ Memulai Perekaman...');
    await triggerSTT();
  };

  const handleReset = () => {
    resetAfkTimer();
    setMessages([]);
    setStatusText('Status: Chat direset');
  };

  const handleUpdateSettings = async (newSettings) => {
    setSettings((prev) => ({ ...prev, ...newSettings }));
    await updateSettings(newSettings);
  };

  const handleAddMemory = async (fact, category) => {
    resetAfkTimer();
    const res = await addMemory(fact, category);
    if (res && res.memories) {
      setMemories(res.memories);
    }
  };

  const handleDeleteMemory = async (memoryId) => {
    resetAfkTimer();
    const res = await deleteMemory(memoryId);
    if (res && res.memories) {
      setMemories(res.memories);
    }
  };

  const handleClearMemories = async () => {
    resetAfkTimer();
    const res = await clearMemories();
    if (res && res.memories) {
      setMemories(res.memories);
    }
  };

  // Determine current cat pose based on application state machine
  const getCatPose = () => {
    if (isWindowMoving) return 'lifted';
    if (isAiSpeaking) return 'licking';
    if (isAiThinking) return 'sit_backward';
    if (isMicActive) return 'sit_forward';
    if (isCollapsed || isAfkSleeping) return 'sleeping';
    return 'sit_forward';
  };

  const currentTheme = settings.theme || 'theme-mocha';
  const currentCatId = settings.selected_cat || 'cat_01';

  return (
    <div
      className={`app-root ${currentTheme}`}
      data-theme={currentTheme}
      onDoubleClick={(e) => e.preventDefault()}
    >
      <div className={`main-window ${isCollapsed ? 'collapsed-window' : ''}`}>
        {!isCollapsed && (
          <div className="chat-container">
            <Header
              currentView={currentView}
              onSelectView={(view) => setCurrentView(view)}
              onReset={handleReset}
              onStartDrag={() => setIsWindowMoving(true)}
              onEndDrag={() => setIsWindowMoving(false)}
            />

            {currentView === 'chat' && (
              <ChatPanel
                messages={messages}
                onSendMessage={handleSendMessage}
                onStartMic={handleStartMic}
                statusText={statusText}
                isMicActive={isMicActive}
              />
            )}

            {currentView === 'memory' && (
              <MemoryPanel
                memories={memories}
                onAddMemory={handleAddMemory}
                onDeleteMemory={handleDeleteMemory}
                onClearMemories={handleClearMemories}
                onBackToChat={() => setCurrentView('chat')}
              />
            )}

            {currentView === 'settings' && (
              <SettingsPanel
                settings={settings}
                onUpdateSettings={handleUpdateSettings}
                onBackToChat={() => setCurrentView('chat')}
              />
            )}
          </div>
        )}

        <PetWidget
          isCollapsed={isCollapsed}
          onToggleCollapse={() => {
            resetAfkTimer();
            setIsCollapsed(!isCollapsed);
          }}
          catId={currentCatId}
          currentPose={getCatPose()}
          isWindowMoving={isWindowMoving}
          status={isMicActive ? 'listening' : isAiThinking ? 'thinking' : 'idle'}
        />
      </div>
    </div>
  );
}
