/* VK 2010-style audio player.
 *
 * One global Audio() instance. Header player ("topbar-player") shows the
 * current track and survives HTMX-boosted navigation. Track rows on the
 * audio pages mirror the header state for the row whose data-src matches
 * the player's src.
 */
(function () {
  const audio = new Audio();
  audio.preload = 'none';
  let currentSrc = null;

  function $(id) { return document.getElementById(id); }

  function fmt(t) {
    if (!isFinite(t)) return '0:00';
    const m = Math.floor(t / 60);
    const s = Math.floor(t % 60).toString().padStart(2, '0');
    return m + ':' + s;
  }

  function visibleRowFor(src) {
    return document.querySelector('.audio-row[data-src="' + CSS.escape(src) + '"]');
  }

  function paintHeader() {
    const bar = $('topbar-player');
    if (!bar) return;
    if (!currentSrc) {
      bar.hidden = true;
      return;
    }
    bar.hidden = false;
    $('player-toggle').textContent = audio.paused ? '▶' : '❚❚';
    const dur = audio.duration || 0;
    $('player-progress-fill').style.width = (dur ? (audio.currentTime / dur) * 100 : 0) + '%';
    $('player-time').textContent = fmt(audio.currentTime) + (dur ? ' / ' + fmt(dur) : '');
  }

  function paintRows() {
    document.querySelectorAll('.audio-row').forEach(function (row) {
      const isCurrent = currentSrc && row.dataset.src === currentSrc;
      const btn = row.querySelector('.audio-play');
      const fill = row.querySelector('.audio-progress-fill');
      const time = row.querySelector('.audio-time');
      if (!btn) return;
      if (isCurrent) {
        btn.textContent = audio.paused ? '▶' : '❚❚';
        btn.classList.toggle('playing', !audio.paused);
        const dur = audio.duration || 0;
        if (fill) fill.style.width = (dur ? (audio.currentTime / dur) * 100 : 0) + '%';
        if (time) time.textContent = fmt(audio.currentTime) + (dur ? ' / ' + fmt(dur) : '');
      } else {
        btn.textContent = '▶';
        btn.classList.remove('playing');
        if (fill) fill.style.width = '0%';
        if (time) time.textContent = '0:00';
      }
    });
  }

  function paint() { paintHeader(); paintRows(); }

  function setHeaderTitle(artist, title) {
    const el = $('player-title');
    if (el) el.innerHTML = '<b>' + escapeHTML(artist) + '</b> — ' + escapeHTML(title);
  }

  function escapeHTML(s) {
    return (s || '').replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function playFromRow(row) {
    const src = row.dataset.src;
    if (currentSrc === src) {
      if (audio.paused) audio.play(); else audio.pause();
      return;
    }
    currentSrc = src;
    audio.src = src;
    setHeaderTitle(row.dataset.artist, row.dataset.title);
    audio.play();
  }

  function togglePause() {
    if (!currentSrc) return;
    if (audio.paused) audio.play(); else audio.pause();
  }

  function close() {
    audio.pause();
    audio.removeAttribute('src');
    audio.load();
    currentSrc = null;
    paint();
  }

  audio.addEventListener('timeupdate', paint);
  audio.addEventListener('play', paint);
  audio.addEventListener('pause', paint);
  audio.addEventListener('loadedmetadata', paint);
  audio.addEventListener('ended', function () {
    audio.currentTime = 0;
    paint();
  });

  document.addEventListener('click', function (e) {
    const playBtn = e.target.closest('.audio-play');
    if (playBtn) {
      const row = playBtn.closest('.audio-row');
      if (row) playFromRow(row);
      return;
    }
    if (e.target.closest('#player-toggle')) {
      togglePause();
      return;
    }
    if (e.target.closest('#player-close')) {
      close();
      return;
    }
    const headerBar = e.target.closest('#player-progress');
    if (headerBar && audio.duration) {
      const r = headerBar.getBoundingClientRect();
      audio.currentTime = ((e.clientX - r.left) / r.width) * audio.duration;
      return;
    }
    const rowBar = e.target.closest('.audio-progress');
    if (rowBar) {
      const row = rowBar.closest('.audio-row');
      if (row && row.dataset.src === currentSrc && audio.duration) {
        const r = rowBar.getBoundingClientRect();
        audio.currentTime = ((e.clientX - r.left) / r.width) * audio.duration;
      }
    }
  });

  // After HTMX swap (boost navigation), re-paint visible rows.
  document.body.addEventListener('htmx:afterSettle', paint);
  // Also after first DOM ready.
  if (document.readyState !== 'loading') paint();
  else document.addEventListener('DOMContentLoaded', paint);
})();
