import React, { useState } from 'react';
import { Brain, Plus, Trash2, Sparkles, User, Heart, Clock, Bookmark, RotateCcw } from 'lucide-react';

const CATEGORIES = [
  { id: 'identity', label: 'Identitas', icon: User, color: 'var(--accent-pink)' },
  { id: 'preference', label: 'Preferensi', icon: Heart, color: 'var(--accent-yellow)' },
  { id: 'habit', label: 'Kebiasaan', icon: Clock, color: 'var(--accent-blue)' },
  { id: 'general', label: 'Umum', icon: Bookmark, color: 'var(--accent-green)' },
];

export default function MemoryPanel({
  memories = [],
  onAddMemory,
  onDeleteMemory,
  onClearMemories,
  onBackToChat,
}) {
  const [newFact, setNewFact] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('general');
  const [activeFilter, setActiveFilter] = useState('all');

  const handleAddSubmit = (e) => {
    e.preventDefault();
    if (!newFact.trim()) return;
    onAddMemory(newFact.trim(), selectedCategory);
    setNewFact('');
  };

  const filteredMemories = memories.filter((m) => {
    if (activeFilter === 'all') return true;
    return (m.category || 'general') === activeFilter;
  });

  const getCategoryMeta = (catId) => {
    return CATEGORIES.find((c) => c.id === catId) || CATEGORIES[3];
  };

  return (
    <div className="memory-panel">
      <div className="memory-header">
        <div className="memory-header-title">
          <Brain size={18} className="memory-icon-header" />
          <h3>Memori & Habit AI ({memories.length})</h3>
        </div>
        {memories.length > 0 && (
          <button
            className="btn-clear-all"
            onClick={onClearMemories}
            title="Hapus Semua Memori"
          >
            <RotateCcw size={12} />
            <span>Clear</span>
          </button>
        )}
      </div>

      {/* Form Input Memori Manual */}
      <form onSubmit={handleAddSubmit} className="memory-input-form">
        <input
          type="text"
          value={newFact}
          onChange={(e) => setNewFact(e.target.value)}
          placeholder="Tambah fakta baru (contoh: Hobi saya bermain gitar)..."
          className="memory-input"
        />
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="category-select"
        >
          {CATEGORIES.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.label}
            </option>
          ))}
        </select>
        <button type="submit" className="btn-add-memory" title="Simpan Memori">
          <Plus size={14} />
        </button>
      </form>

      {/* Filter Chips */}
      <div className="filter-chips">
        <button
          className={`chip ${activeFilter === 'all' ? 'active' : ''}`}
          onClick={() => setActiveFilter('all')}
        >
          Semua ({memories.length})
        </button>
        {CATEGORIES.map((cat) => {
          const count = memories.filter((m) => (m.category || 'general') === cat.id).length;
          return (
            <button
              key={cat.id}
              className={`chip ${activeFilter === cat.id ? 'active' : ''}`}
              onClick={() => setActiveFilter(cat.id)}
            >
              {cat.label} ({count})
            </button>
          );
        })}
      </div>

      {/* List Memori */}
      <div className="memory-list-container">
        {filteredMemories.length === 0 ? (
          <div className="memory-empty-state">
            <Sparkles size={28} className="empty-sparkle-icon" />
            <p className="empty-title">
              {activeFilter === 'all'
                ? 'Belum ada memori tersimpan~'
                : `Belum ada fakta kategori ${getCategoryMeta(activeFilter).label}`}
            </p>
            <p className="empty-desc">
              Bicara dengan Kitty tentang dirimu, atau tambahkan fakta baru secara manual di atas!
            </p>
          </div>
        ) : (
          filteredMemories.map((mem) => {
            const meta = getCategoryMeta(mem.category);
            const IconComp = meta.icon;
            return (
              <div key={mem.id} className="memory-card">
                <div className="memory-card-body">
                  <div className="memory-tag" style={{ color: meta.color, borderColor: meta.color }}>
                    <IconComp size={10} />
                    <span>{meta.label}</span>
                  </div>
                  <p className="memory-fact-text">{mem.fact}</p>
                </div>
                <button
                  className="btn-delete-memory"
                  onClick={() => onDeleteMemory(mem.id)}
                  title="Hapus memori ini"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            );
          })
        )}
      </div>

      <button className="btn-back" onClick={onBackToChat}>
        🔙 Kembali ke Chat
      </button>
    </div>
  );
}
