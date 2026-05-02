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

  // Browsers block autoplay until the user interacts. Capture the first
  // click anywhere and "unlock" by playing+immediately pausing.
  let unlocked = false;
  function unlock() {
    if (unlocked) return;
    unlocked = true;
    audio.play().then(() => audio.pause()).catch(() => {});
  }
  document.addEventListener('click', unlock, { once: true, capture: true });
  document.addEventListener('keydown', unlock, { once: true, capture: true });

  let lastCount = null;

  function syncTitle(n) {
    document.title = n > 0 ? '(' + n + ') ' + cfg.baseTitle : cfg.baseTitle;
  }

  function poll() {
    if (document.visibilityState !== 'visible') return;
    fetch(cfg.url, { credentials: 'same-origin', cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data) return;
        const n = data.count | 0;
        if (lastCount !== null && n > lastCount) {
          // count went up — play sound (best-effort, may be blocked
          // until first user gesture).
          try { audio.currentTime = 0; audio.play().catch(() => {}); } catch (e) {}
        }
        lastCount = n;
        syncTitle(n);
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
