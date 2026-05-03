/* Periodically asks the server for the unread message count.
 * Plays a notification sound when the count goes up, and prefixes
 * document.title with "(N) " so the tab badge nudges the user.
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

  function poll() {
    if (document.visibilityState !== 'visible') return;
    fetch(cfg.url, { credentials: 'same-origin', cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data) return;
        const messages = (data.messages != null ? data.messages : data.count) | 0;
        const requests = (data.requests || 0) | 0;
        const news = (data.news || 0) | 0;
        if (lastMessages !== null && messages > lastMessages) {
          // count went up — play sound (best-effort, may be blocked
          // until first user gesture).
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
      })
      .catch(function () {});
  }

  // Initial fire so we capture the baseline + show the badge on load.
  poll();
  setInterval(poll, 10000);

  // Refire when the tab regains focus so we don't wait up to 10s.
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'visible') poll();
  });
})();
