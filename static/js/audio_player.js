/* Single-track audio player matching VK 2010 — only one row plays at a time. */
(function () {
  let current = null; // { row, audio } currently playing
  const audioPool = new WeakMap();

  function fmt(t) {
    if (!isFinite(t)) return '0:00';
    const m = Math.floor(t / 60);
    const s = Math.floor(t % 60).toString().padStart(2, '0');
    return m + ':' + s;
  }

  function audioFor(row) {
    let a = audioPool.get(row);
    if (a) return a;
    a = new Audio(row.dataset.src);
    a.preload = 'none';
    const fill = row.querySelector('.audio-progress-fill');
    const time = row.querySelector('.audio-time');
    const btn = row.querySelector('.audio-play');
    a.addEventListener('timeupdate', function () {
      const dur = a.duration || 0;
      fill.style.width = (dur ? (a.currentTime / dur) * 100 : 0) + '%';
      time.textContent = fmt(a.currentTime) + (dur ? ' / ' + fmt(dur) : '');
    });
    a.addEventListener('loadedmetadata', function () {
      time.textContent = '0:00 / ' + fmt(a.duration);
    });
    a.addEventListener('ended', function () {
      btn.textContent = '▶';
      btn.classList.remove('playing');
      fill.style.width = '0%';
      if (current && current.audio === a) current = null;
    });
    audioPool.set(row, a);
    return a;
  }

  function stop(entry) {
    entry.audio.pause();
    entry.row.querySelector('.audio-play').textContent = '▶';
    entry.row.querySelector('.audio-play').classList.remove('playing');
  }

  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.audio-play');
    if (btn) {
      const row = btn.closest('.audio-row');
      const audio = audioFor(row);
      if (current && current.row === row) {
        stop(current);
        current = null;
      } else {
        if (current) stop(current);
        audio.play();
        btn.textContent = '❚❚';
        btn.classList.add('playing');
        current = { row: row, audio: audio };
      }
      return;
    }

    const bar = e.target.closest('.audio-progress');
    if (bar) {
      const row = bar.closest('.audio-row');
      const audio = audioFor(row);
      const rect = bar.getBoundingClientRect();
      const ratio = (e.clientX - rect.left) / rect.width;
      if (audio.duration) audio.currentTime = ratio * audio.duration;
    }
  });
})();
