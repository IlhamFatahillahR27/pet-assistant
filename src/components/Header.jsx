import React from 'react';
import { RotateCcw, Settings, MessageSquare, Brain, Power } from 'lucide-react';
import { getCurrentWindow } from '@tauri-apps/api/window';

export default function Header({
  currentView,
  onSelectView,
  onReset,
  onStartDrag,
  onEndDrag,
}) {
  const handleDrag = async (e) => {
    if (e.button === 0 && !e.target.closest('.header-actions')) {
      onStartDrag?.();
      try {
        const appWindow = getCurrentWindow();
        await appWindow.startDragging();
      } catch (err) {
        console.warn('Window drag notice:', err);
      } finally {
        onEndDrag?.();
      }
    }
  };

  const handleCloseApp = async () => {
    try {
      try {
        await fetch('http://127.0.0.1:8000/api/system/shutdown', { method: 'POST' });
      } catch (_) {}
      const appWindow = getCurrentWindow();
      await appWindow.close();
    } catch (err) {
      console.warn('App close notice:', err);
      window.close();
    }
  };

  return (
    <div className="app-header" onPointerDown={handleDrag} data-tauri-drag-region>
      <div className="header-title" data-tauri-drag-region>
        <span className="cat-icon">🐈</span>
        <span className="title-text">Pet Assistant</span>
      </div>

      <div className="header-actions">
        <button
          className="btn-header btn-reset"
          onClick={onReset}
          title="Reset Chat Session"
        >
          <RotateCcw size={13} />
        </button>

        <button
          className={`btn-header ${currentView === 'chat' ? 'active' : ''}`}
          onClick={() => onSelectView('chat')}
          title="Tampilan Chat"
        >
          <MessageSquare size={13} />
        </button>

        <button
          className={`btn-header ${currentView === 'memory' ? 'active' : ''}`}
          onClick={() => onSelectView('memory')}
          title="Memori & Habit AI"
        >
          <Brain size={13} />
        </button>

        <button
          className={`btn-header ${currentView === 'settings' ? 'active' : ''}`}
          onClick={() => onSelectView('settings')}
          title="Pengaturan"
        >
          <Settings size={13} />
        </button>

        <button
          className="btn-header btn-close-app"
          onClick={handleCloseApp}
          title="Tutup & Matikan Aplikasi"
        >
          <Power size={13} />
        </button>
      </div>
    </div>
  );
}
