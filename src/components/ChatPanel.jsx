import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic } from 'lucide-react';

function formatMessageContent(text) {
  if (!text) return null;

  const lines = text.split('\n');
  return lines.map((line, lineIdx) => {
    let content = line.trim();
    if (!content) return <div key={lineIdx} className="msg-spacer" />;

    let isHeader = false;
    let isBullet = false;

    if (content.startsWith('### ') || content.startsWith('## ') || content.startsWith('# ')) {
      content = content.replace(/^#+\s*/, '');
      isHeader = true;
    } else if (content.startsWith('* ') || content.startsWith('- ')) {
      content = content.replace(/^[*\-]\s*/, '');
      isBullet = true;
    }

    // Process bold **text** and inline math $math$
    const parts = content.split(/(\*\*.*?\*\*|\$.*?\$)/g);
    const renderedParts = parts.map((part, pIdx) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={pIdx}>{part.slice(2, -2)}</strong>;
      } else if (part.startsWith('$') && part.endsWith('$')) {
        return <code key={pIdx} className="inline-math">{part.slice(1, -1)}</code>;
      }
      return part;
    });

    if (isHeader) {
      return (
        <div key={lineIdx} className="msg-header">
          {renderedParts}
        </div>
      );
    }
    if (isBullet) {
      return (
        <div key={lineIdx} className="msg-bullet">
          <span className="bullet-dot">•</span>
          <span className="bullet-text">{renderedParts}</span>
        </div>
      );
    }
    return (
      <div key={lineIdx} className="msg-paragraph">
        {renderedParts}
      </div>
    );
  });
}

export default function ChatPanel({
  messages,
  onSendMessage,
  onStartMic,
  statusText,
  isMicActive,
}) {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    onSendMessage(inputText.trim());
    setInputText('');
  };

  return (
    <div className="chat-panel">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p className="welcome-title">✨ Halo! Saya Pet Assistant Anda.</p>
            <p className="welcome-subtitle">
              Sapa saya dengan <strong>"Hi Kitty"</strong>, <strong>"Mew Mew"</strong>, atau <strong>"Hey Kitty"</strong>!
            </p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`message-bubble ${msg.sender === 'Anda' ? 'user-msg' : 'bot-msg'}`}
            >
              <div className="message-sender">{msg.sender}</div>
              <div className="message-text">{formatMessageContent(msg.text)}</div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="status-bar">
        <span className="status-dot"></span>
        <span className="status-text">{statusText || 'Status: Idle'}</span>
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          placeholder="Ketik pesan..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
        />
        <button type="submit" className="btn-send" title="Kirim Pesan">
          <Send size={16} />
        </button>
      </form>

      <button
        type="button"
        className={`btn-mic ${isMicActive ? 'mic-active' : ''}`}
        onClick={onStartMic}
        disabled={isMicActive}
      >
        <Mic size={18} />
        <span>{isMicActive ? '🎙️ Mendengarkan...' : '🎤 Tanya Asisten'}</span>
      </button>
    </div>
  );
}
