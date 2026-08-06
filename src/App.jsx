import React, { useState, useEffect } from 'react';
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

export default function App() {
  const [currentView, setCurrentView] = useState('chat'); // 'chat', 'memory', 'settings'
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [messages, setMessages] = useState([]);
  const [memories, setMemories] = useState([]);
  const [statusText, setStatusText] = useState('Status: Idle');
  const [isMicActive, setIsMicActive] = useState(false);
  const [settings, setSettings] = useState({
    tts: { enabled: true, rate: 170 },
    wake_word: { enabled: true },
  });

  useEffect(() => {
    // 0. Set initial position at bottom-right of the screen
    const initPosition = async () => {
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
    };
    initPosition();

    // 1. Fetch initial settings & memories
    fetchSettings().then((res) => {
      if (res) setSettings(res);
    });

    fetchMemories().then((mems) => {
      if (mems) setMemories(mems);
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
      setStatusText(`🎙️ Kata Pemicu '${data.model}' Terdeteksi!`);
      triggerSTT();
    });

    const unsubSTTStatus = wsClient.on('stt_status', (data) => {
      if (data.status === 'listening') {
        setIsMicActive(true);
        setStatusText('🎙️ Silakan Berbicara...');
      } else if (data.status === 'processing') {
        setStatusText('🤖 Memproses Suara...');
      } else if (data.status === 'recognized') {
        setIsMicActive(false);
        setMessages((prev) => [...prev, { sender: 'Anda', text: data.text }]);
        setStatusText('🤖 Berpikir...');
      } else if (data.status === 'error') {
        setIsMicActive(false);
        setStatusText(`Status: Error (${data.error})`);
      }
    });

    const unsubChatChunk = wsClient.on('chat_chunk', (data) => {
      if (data.done) {
        if (data.full_text) {
          setMessages((prev) => {
            const filtered = prev.filter((m) => !m.isStreaming);
            return [...filtered, { sender: 'Asisten', text: data.full_text }];
          });
        }
        setStatusText('Status: Idle');
        setIsMicActive(false);
      } else if (data.text) {
        setStatusText('🤖 Menjawab...');
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

    return () => {
      unsubConnected();
      unsubDisconnected();
      unsubWakeword();
      unsubSTTStatus();
      unsubChatChunk();
      unsubMemoryUpdated();
    };
  }, []);

  const handleSendMessage = async (text) => {
    setMessages((prev) => [...prev, { sender: 'Anda', text }]);
    setStatusText('🤖 Berpikir...');

    // Kirim via WebSocket jika terhubung, fallback ke REST
    if (wsClient.isConnected) {
      wsClient.send('chat', { prompt: text });
    } else {
      const res = await sendChatMessage(text);
      if (res && res.response) {
        setMessages((prev) => [...prev, { sender: 'Asisten', text: res.response }]);
        setStatusText('Status: Idle');
      } else {
        setStatusText('Status: Error mengirim pesan');
      }
    }
  };

  const handleStartMic = async () => {
    setIsMicActive(true);
    setStatusText('🎙️ Memulai Perekaman...');
    await triggerSTT();
  };

  const handleReset = () => {
    setMessages([]);
    setStatusText('Status: Chat direset');
  };

  const handleUpdateSettings = async (newSettings) => {
    setSettings((prev) => ({ ...prev, ...newSettings }));
    await updateSettings(newSettings);
  };

  const handleAddMemory = async (fact, category) => {
    const res = await addMemory(fact, category);
    if (res && res.memories) {
      setMemories(res.memories);
    }
  };

  const handleDeleteMemory = async (memoryId) => {
    const res = await deleteMemory(memoryId);
    if (res && res.memories) {
      setMemories(res.memories);
    }
  };

  const handleClearMemories = async () => {
    const res = await clearMemories();
    if (res && res.memories) {
      setMemories(res.memories);
    }
  };

  return (
    <div className="app-root">
      <div className={`main-window ${isCollapsed ? 'collapsed-window' : ''}`}>
        {!isCollapsed && (
          <div className="chat-container">
            <Header
              currentView={currentView}
              onSelectView={(view) => setCurrentView(view)}
              onReset={handleReset}
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
          onToggleCollapse={() => setIsCollapsed(!isCollapsed)}
          status={isMicActive ? 'listening' : 'idle'}
        />
      </div>
    </div>
  );
}
