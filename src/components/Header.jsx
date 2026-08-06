import React from 'react';
import { RotateCcw, Settings, MessageSquare, Brain } from 'lucide-react';
import { getCurrentWindow } from '@tauri-apps/api/window';

export default function Header({ currentView, onSelectView, onReset }) {
  const handleDrag = async (e) => {
    if (e.button === 0 && !e.target.closest('.header-actions')) {
      try {
        const appWindow = getCurrentWindow();
        await appWindow.startDragging();
      } catch (err) {
        console.warn('Window drag notice:', err);
      }
    }
  };

  return (
    <div className="app-header" onMouseDown={handleDrag} data-tauri-drag-region>
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
      </div>
    </div>
  );
}
