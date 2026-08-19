import React, { useState, useEffect, useRef } from 'react';
import FrameAnimator from './FrameAnimator';
import { getCurrentWindow } from '@tauri-apps/api/window';

export default function PetWidget({
  isCollapsed,
  onToggleCollapse,
  catId = 'cat_01',
  currentPose = 'sit_forward',
  isWindowMoving = false,
  status = 'idle',
}) {
  const [isLifted, setIsLifted] = useState(false);
  const [temporaryPose, setTemporaryPose] = useState(null);
  const dragInfo = useRef({ isDragging: false, startX: 0, startY: 0, startTime: 0 });
  const tempPoseTimer = useRef(null);

  // Global mouseup / pointerup to ensure lifted state resets when mouse is released anywhere
  useEffect(() => {
    const handleGlobalRelease = () => {
      if (dragInfo.current.isDragging || isLifted) {
        dragInfo.current.isDragging = false;
        setIsLifted(false);
      }
    };

    window.addEventListener('mouseup', handleGlobalRelease);
    window.addEventListener('pointerup', handleGlobalRelease);
    window.addEventListener('mouseleave', handleGlobalRelease);
    window.addEventListener('blur', handleGlobalRelease);

    return () => {
      window.removeEventListener('mouseup', handleGlobalRelease);
      window.removeEventListener('pointerup', handleGlobalRelease);
      window.removeEventListener('mouseleave', handleGlobalRelease);
      window.removeEventListener('blur', handleGlobalRelease);
    };
  }, [isLifted]);

  // Sync with isWindowMoving from App.jsx
  useEffect(() => {
    if (isWindowMoving) {
      setIsLifted(true);
    }
  }, [isWindowMoving]);

  const handleMouseDown = async (e) => {
    if (e.button !== 0) return; // Only left click

    dragInfo.current = {
      isDragging: true,
      startX: e.clientX,
      startY: e.clientY,
      startTime: Date.now(),
    };

    // INSTANTLY activate 'lifted' pose when mouse touches down on the cat
    setIsLifted(true);

    try {
      const appWindow = getCurrentWindow();
      // Start native Tauri dragging (blocks until user drops the window)
      await appWindow.startDragging();
    } catch (err) {
      console.warn('PetWidget window drag notice:', err);
    } finally {
      // Once native drag finishes (mouse released)
      const duration = Date.now() - dragInfo.current.startTime;
      const dx = Math.abs(e.clientX - dragInfo.current.startX);
      const dy = Math.abs(e.clientY - dragInfo.current.startY);

      dragInfo.current.isDragging = false;
      setIsLifted(false);

      // If it was a quick tap/click (< 250ms and minimal movement), toggle collapse
      if (duration < 250 && dx < 8 && dy < 8) {
        setTemporaryPose('hide_n_seek');
        if (tempPoseTimer.current) clearTimeout(tempPoseTimer.current);
        tempPoseTimer.current = setTimeout(() => {
          setTemporaryPose(null);
        }, 1000);

        onToggleCollapse();
      }
    }
  };

  // Determine active pose:
  // 1. If lifted (pointer down or window moving or currentPose === 'lifted') -> 'lifted'
  // 2. Temporary pose (e.g. peek/hide_n_seek on quick tap)
  // 3. Current pose from App state (sit_forward, sit_backward, licking, sleeping)
  const isBeingLifted = isLifted || isWindowMoving || currentPose === 'lifted';
  const activePose = isBeingLifted ? 'lifted' : (temporaryPose || currentPose);

  return (
    <div
      className={`pet-widget-container ${isCollapsed ? 'collapsed' : ''}`}
      onMouseDown={handleMouseDown}
      title="Tahan untuk mengangkat & memindahkan posisi / Klik untuk sembunyikan"
      style={{ cursor: isBeingLifted ? 'grabbing' : 'grab' }}
      data-tauri-drag-region
    >
      <div className="cat-avatar-wrapper" data-tauri-drag-region>
        <FrameAnimator
          catId={catId}
          pose={activePose}
          className="cat-gif"
        />
        {status === 'listening' && <div className="listening-pulse"></div>}
      </div>
    </div>
  );
}
