import React from 'react';
import { RotateCcw, Settings, MessageSquare } from 'lucide-react';
import { getCurrentWindow } from '@tauri-apps/api/window';

export default function Header({ currentView, toggleView, onReset }) {
  const handleDrag = async (e) => {
    // Only drag on left click and when not clicking on action buttons
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
          <span>Reset</span>
        </button>

        <button
          className={`btn-header btn-toggle-view ${currentView === 'settings' ? 'active' : ''}`}
          onClick={toggleView}
          title={currentView === 'chat' ? 'Buka Pengaturan' : 'Kembali ke Chat'}
        >
          {currentView === 'chat' ? (
            <Settings size={14} />
          ) : (
            <MessageSquare size={14} />
          )}
        </button>
      </div>
    </div>
  );
}
