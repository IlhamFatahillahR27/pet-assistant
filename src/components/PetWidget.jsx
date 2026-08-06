import React, { useRef } from 'react';
import catGif from '../assets/orange-cat.gif';
import { getCurrentWindow } from '@tauri-apps/api/window';

export default function PetWidget({ isCollapsed, onToggleCollapse, status }) {
  const dragInfo = useRef({ isDragging: false, startX: 0, startY: 0 });

  const handleMouseDown = async (e) => {
    if (e.button !== 0) return;
    dragInfo.current = {
      isDragging: false,
      startX: e.clientX,
      startY: e.clientY,
    };

    try {
      const appWindow = getCurrentWindow();
      await appWindow.startDragging();
    } catch (err) {
      console.warn('PetWidget window drag notice:', err);
    }
  };

  const handleClick = (e) => {
    // If movement was minimal, treat as a click to toggle collapse
    const dx = Math.abs(e.clientX - dragInfo.current.startX);
    const dy = Math.abs(e.clientY - dragInfo.current.startY);
    if (dx < 5 && dy < 5) {
      onToggleCollapse();
    }
  };

  return (
    <div
      className={`pet-widget-container ${isCollapsed ? 'collapsed' : ''}`}
      onMouseDown={handleMouseDown}
      onClick={handleClick}
      title="Klik untuk meminimalkan / geser untuk memindahkan widget"
      data-tauri-drag-region
    >
      <div className="cat-avatar-wrapper" data-tauri-drag-region>
        <img
          src={catGif}
          alt="Orange Cat Assistant"
          className="cat-gif"
          data-tauri-drag-region
        />
        {status === 'listening' && <div className="listening-pulse"></div>}
      </div>
    </div>
  );
}
