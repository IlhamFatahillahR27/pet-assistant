import React, { useState, useEffect, useRef } from 'react';
import { CAT_SKINS, getCatFrameUrl } from '../config/catRegistry';

/**
 * FrameAnimator Component
 * Handles smooth frame-by-frame PNG sequence playback with preloading and customizable FPS.
 */
export default function FrameAnimator({
  catId = 'cat_01',
  pose = 'sit_forward',
  className = '',
  alt = 'Cat Assistant',
}) {
  const [frameIndex, setFrameIndex] = useState(1);
  const preloadedImages = useRef(new Map());
  const timerRef = useRef(null);

  const catConfig = CAT_SKINS[catId] || CAT_SKINS.cat_01;
  const poseConfig = catConfig.poses[pose] || catConfig.poses.sit_forward;
  const totalFrames = poseConfig?.frameCount || 10;
  const fps = poseConfig?.fps || 8;
  const frameInterval = Math.max(30, Math.round(1000 / fps));

  // Preload all frames for current catId and pose
  useEffect(() => {
    setFrameIndex(1); // Reset frame counter on pose or cat change

    const preloadKeyPrefix = `${catId}_${pose}`;
    for (let i = 1; i <= totalFrames; i++) {
      const cacheKey = `${preloadKeyPrefix}_${i}`;
      if (!preloadedImages.current.has(cacheKey)) {
        const img = new Image();
        img.src = getCatFrameUrl(catId, pose, i);
        preloadedImages.current.set(cacheKey, img);
      }
    }
  }, [catId, pose, totalFrames]);

  // Frame animation loop
  useEffect(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    timerRef.current = setInterval(() => {
      setFrameIndex((prevIndex) => {
        if (prevIndex >= totalFrames) {
          return 1; // loop back to start
        }
        return prevIndex + 1;
      });
    }, frameInterval);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [catId, pose, totalFrames, frameInterval]);

  const currentSrc = getCatFrameUrl(catId, pose, frameIndex);

  return (
    <img
      src={currentSrc}
      alt={alt}
      className={`cat-frame-sprite ${className}`}
      draggable={false}
    />
  );
}
