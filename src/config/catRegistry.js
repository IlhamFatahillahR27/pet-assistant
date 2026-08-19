/**
 * Cat Registry & Theme Configuration
 * Phase 6: Frame-by-frame animation, Cat Skins & UI Themes
 */

export const CAT_SKINS = {
  cat_01: {
    id: 'cat_01',
    name: 'Orange Tabby (Oyen)',
    description: 'Kucing oranye ceria, ramah & penuh energi',
    preview: '/assets/cats/cat_01/sit_forward/01.png',
    poses: {
      hide_n_seek: { frameCount: 10, fps: 8, loop: true },
      licking: { frameCount: 12, fps: 10, loop: true },
      lifted: { frameCount: 12, fps: 12, loop: true },
      sit_backward: { frameCount: 12, fps: 8, loop: true },
      sit_forward: { frameCount: 12, fps: 3, loop: true },
      sleeping: { frameCount: 12, fps: 6, loop: true },
    },
  },
  cat_02: {
    id: 'cat_02',
    name: 'Tuxedo Black (Kuro)',
    description: 'Kucing hitam anggun, tenang & misterius',
    preview: '/assets/cats/cat_02/sit_forward/01.png',
    poses: {
      hide_n_seek: { frameCount: 10, fps: 8, loop: true },
      licking: { frameCount: 10, fps: 10, loop: true },
      lifted: { frameCount: 12, fps: 12, loop: true },
      sit_backward: { frameCount: 10, fps: 8, loop: true },
      sit_forward: { frameCount: 10, fps: 3, loop: true },
      sleeping: { frameCount: 12, fps: 6, loop: true },
    },
  },
};

export const UI_THEMES = [
  {
    id: 'theme-mocha',
    name: 'Catppuccin Mocha',
    description: 'Nuansa gelap elegan & aksen pastel lembut',
    badgeColor: '#89b4fa',
  },
  {
    id: 'theme-cyberpunk',
    name: 'Cyberpunk Neon',
    description: 'Warna futuristik neon cyan & yellow glow',
    badgeColor: '#00f0ff',
  },
  {
    id: 'theme-sakura',
    name: 'Kawaii Sakura',
    description: 'Nuansa pastel pink & sentuhan manis',
    badgeColor: '#f4a6b8',
  },
  {
    id: 'theme-ocean',
    name: 'Nordic Ocean',
    description: 'Nuansa biru laut dalam & sejuk',
    badgeColor: '#58a6ff',
  },
  {
    id: 'theme-emerald',
    name: 'Midnight Emerald',
    description: 'Nuansa hijau zamrud gelap & mewah',
    badgeColor: '#2ea043',
  },
];

/**
 * Mendapatkan URL path ke file frame 2 digit (01.png, 02.png, dst.)
 */
export function getCatFrameUrl(catId, pose, frameNumber) {
  const paddedIndex = String(frameNumber).padStart(2, '0');
  return `/assets/cats/${catId}/${pose}/${paddedIndex}.png`;
}

/**
 * Mendapatkan seluruh daftar URL frame untuk kombinasi skin dan pose tertentu
 */
export function getCatPoseFrames(catId, pose) {
  const cat = CAT_SKINS[catId] || CAT_SKINS.cat_01;
  const poseConfig = cat.poses[pose] || cat.poses.sit_forward;
  const count = poseConfig?.frameCount || 10;

  const frames = [];
  for (let i = 1; i <= count; i++) {
    frames.push(getCatFrameUrl(cat.id, pose, i));
  }
  return frames;
}
