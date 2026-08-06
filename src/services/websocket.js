class WebSocketClient {
  constructor(url = 'ws://127.0.0.1:8000/ws') {
    this.url = url;
    this.ws = null;
    this.listeners = new Map();
    this.isConnected = false;
    this.reconnectTimer = null;
  }

  connect() {
    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('[WebSocket] Terhubung ke Pet Assistant Backend');
        this.isConnected = true;
        this.emit('connected', { isConnected: true });
        this.startHeartbeat();
      };

      this.ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const { event: eventName, data } = payload;
          if (eventName === 'pong') {
            // Heartbeat ACK
            return;
          }
          if (eventName) {
            this.emit(eventName, data);
          }
        } catch (err) {
          console.error('[WebSocket] Gagal parse pesan:', err);
        }
      };

      this.ws.onclose = () => {
        console.log('[WebSocket] Koneksi terputus, mencoba terhubung kembali...');
        this.stopHeartbeat();
        this.isConnected = false;
        this.emit('disconnected', { isConnected: false });
        this.scheduleReconnect();
      };

      this.ws.onerror = (err) => {
        console.error('[WebSocket Error]', err);
        this.ws.close();
      };
    } catch (err) {
      console.error('[WebSocket Connection Error]', err);
      this.scheduleReconnect();
    }
  }

  startHeartbeat() {
    this.stopHeartbeat();
    this.pingTimer = setInterval(() => {
      if (this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send('ping');
      }
    }, 10000);
  }

  stopHeartbeat() {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }

  scheduleReconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, 3000);
  }

  send(action, data = {}) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action, ...data }));
    } else {
      console.warn('[WebSocket] Tidak dapat mengirim pesan, koneksi belum terbuka');
    }
  }

  on(eventName, callback) {
    if (!this.listeners.has(eventName)) {
      this.listeners.set(eventName, new Set());
    }
    this.listeners.get(eventName).add(callback);
    return () => this.off(eventName, callback);
  }

  off(eventName, callback) {
    if (this.listeners.has(eventName)) {
      this.listeners.get(eventName).delete(callback);
    }
  }

  emit(eventName, data) {
    if (this.listeners.has(eventName)) {
      this.listeners.get(eventName).forEach((cb) => cb(data));
    }
  }
}

export const wsClient = new WebSocketClient();
