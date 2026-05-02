/* VK 2010-style audio player.
 *
 * One global Audio() instance. Header player lives in the topbar and
 * survives HTMX-boosted navigation. Track rows on the audio pages
 * mirror the header state for the row whose data-src matches the
 * player's src. A "playlist" snapshot is captured each time the user
 * starts a new track from a list, enabling prev/next/auto-advance.
 *
 * On every track start we POST /audio/now-playing/<id>/ so the user's
 * profile shows "♪ Слушает: ..." for others.
 */
(function () {
  const audio = new Audio();
  audio.preload = 'none';
  let currentSrc = null;
  let currentTrackId = null;
  let playlist = []; // [{src, artist, title, id}]
  let currentIndex = -1;

  function $(id) { return document.getElementById(id); }

  function fmt(t) {
    if (!isFinite(t)) return '0:00';
    const m = Math.floor(t / 60);
    const s = Math.floor(t % 60).toString().padStart(2, '0');
    return m + ':' + s;
  }

  function escapeHTML(s) {
    return (s || '').replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function csrfToken() {
    const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  }

  function pingNowPlaying(trackId) {
    if (!trackId) return;
    fetch('/audio/now-playing/' + trackId + '/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'X-CSRFToken': csrfToken() },
    }).catch(function () {});
  }

  function clearNowPlaying() {
    fetch('/audio/now-playing/clear/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'X-CSRFToken': csrfToken() },
    }).catch(function () {});
  }

  function rowsToTracks() {
    return Array.from(document.querySelectorAll('.audio-row')).map(function (r) {
      return {
        src: r.dataset.src,
        id: r.dataset.trackId,
        artist: r.dataset.artist,
        title: r.dataset.title,
      };
    });
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
    $('player-prev').disabled = currentIndex <= 0;
    $('player-next').disabled = currentIndex < 0 || currentIndex >= playlist.length - 1;
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

  function loadAndPlay(track) {
    currentSrc = track.src;
    currentTrackId = track.id;
    audio.src = track.src;
    setHeaderTitle(track.artist, track.title);
    audio.play();
    pingNowPlaying(track.id);
  }

  function playFromRow(row) {
    const src = row.dataset.src;
    if (currentSrc === src) {
      if (audio.paused) audio.play(); else audio.pause();
      return;
    }
    playlist = rowsToTracks();
    currentIndex = playlist.findIndex(function (t) { return t.src === src; });
    loadAndPlay(playlist[currentIndex]);
  }

  function gotoIndex(i) {
    if (i < 0 || i >= playlist.length) return;
    currentIndex = i;
    loadAndPlay(playlist[i]);
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
    currentTrackId = null;
    playlist = [];
    currentIndex = -1;
    clearNowPlaying();
    paint();
  }

  audio.addEventListener('timeupdate', paint);
  audio.addEventListener('play', paint);
  audio.addEventListener('pause', paint);
  audio.addEventListener('loadedmetadata', paint);
  audio.addEventListener('ended', function () {
    if (currentIndex < playlist.length - 1) {
      gotoIndex(currentIndex + 1);
    } else {
      audio.currentTime = 0;
      paint();
    }
  });

  document.addEventListener('click', function (e) {
    const playBtn = e.target.closest('.audio-play');
    if (playBtn) {
      const row = playBtn.closest('.audio-row');
      if (row) playFromRow(row);
      return;
    }
    if (e.target.closest('#player-toggle')) { togglePause(); return; }
    if (e.target.closest('#player-prev'))   { gotoIndex(currentIndex - 1); return; }
    if (e.target.closest('#player-next'))   { gotoIndex(currentIndex + 1); return; }
    if (e.target.closest('#player-close'))  { close(); return; }
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

  document.body.addEventListener('htmx:afterSettle', paint);
  if (document.readyState !== 'loading') paint();
  else document.addEventListener('DOMContentLoaded', paint);
})();
