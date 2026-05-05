/* Live notification counters via WebSocket.
 * Connects to /ws/notif/ — server pushes {messages, requests, news}
 * snapshots whenever any of those change. Plays a sound when messages
 * or friend-requests go up, prefixes document.title with "(N) ", and
 * updates [data-counter="messages"|"requests"|"news"] sidebar badges.
 *
 * Only runs for authenticated users (the {% if %} in base.html guards
 * the bootstrap window.__DVORIK_NOTIF__).
 */
(function () {
  const cfg = window.__DVORIK_NOTIF__;
  if (!cfg) return;

  const audio = new Audio(cfg.sound);
  audio.preload = 'auto';
  audio.volume = 0.8;
  const requestAudio = cfg.requestSound ? new Audio(cfg.requestSound) : null;
  if (requestAudio) { requestAudio.preload = 'auto'; requestAudio.volume = 0.8; }

  // Browsers block autoplay until the user interacts. Capture the first
  // click anywhere and "unlock" by playing+immediately pausing.
  let unlocked = false;
  function unlock() {
    if (unlocked) return;
    unlocked = true;
    audio.play().then(() => audio.pause()).catch(() => {});
    if (requestAudio) requestAudio.play().then(() => requestAudio.pause()).catch(() => {});
  }
  document.addEventListener('click', unlock, { once: true, capture: true });
  document.addEventListener('keydown', unlock, { once: true, capture: true });

  let lastMessages = null;
  let lastRequests = null;

  function syncTitle(n) {
    document.title = n > 0 ? '(' + n + ') ' + cfg.baseTitle : cfg.baseTitle;
  }

  function syncCounter(name, n) {
    document.querySelectorAll('[data-counter="' + name + '"]').forEach(function (el) {
      el.textContent = n > 0 ? ' (' + n + ')' : '';
    });
  }

  function applySnapshot(data) {
    const messages = (data.messages || 0) | 0;
    const requests = (data.requests || 0) | 0;
    const news = (data.news || 0) | 0;
    if (lastMessages !== null && messages > lastMessages) {
      try { audio.currentTime = 0; audio.play().catch(() => {}); } catch (e) {}
    }
    if (lastRequests !== null && requests > lastRequests && requestAudio) {
      try { requestAudio.currentTime = 0; requestAudio.play().catch(() => {}); } catch (e) {}
    }
    lastMessages = messages;
    lastRequests = requests;
    syncTitle(messages);
    syncCounter('messages', messages);
    syncCounter('requests', requests);
    syncCounter('news', news);
  }

  let ws = null;
  let backoff = 1000;  // ms; doubles each failed reconnect, capped at 30s
  function connect() {
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(proto + '//' + location.host + '/ws/notif/');
    ws.onopen = function () { backoff = 1000; };
    ws.onmessage = function (ev) {
      try { applySnapshot(JSON.parse(ev.data)); } catch (e) {}
    };
    ws.onclose = function () {
      ws = null;
      setTimeout(connect, backoff);
      backoff = Math.min(backoff * 2, 30000);
    };
    ws.onerror = function () { try { ws.close(); } catch (e) {} };
  }
  connect();
})();
