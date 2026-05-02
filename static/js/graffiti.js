(function () {
  const canvas = document.getElementById('graffiti');
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#FFFFFF';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  let color = '#000000';
  let size = 4;
  let drawing = false;
  let lastX = 0, lastY = 0;

  function pos(e) {
    const rect = canvas.getBoundingClientRect();
    const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
    const y = (e.touches ? e.touches[0].clientY : e.clientY) - rect.top;
    return { x: x * canvas.width / rect.width, y: y * canvas.height / rect.height };
  }

  function start(e) {
    e.preventDefault();
    drawing = true;
    const p = pos(e);
    lastX = p.x; lastY = p.y;
    // dot for single click
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(lastX, lastY, size / 2, 0, Math.PI * 2);
    ctx.fill();
  }

  function move(e) {
    if (!drawing) return;
    e.preventDefault();
    const p = pos(e);
    ctx.strokeStyle = color;
    ctx.lineWidth = size;
    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(p.x, p.y);
    ctx.stroke();
    lastX = p.x; lastY = p.y;
  }

  function stop() { drawing = false; }

  canvas.addEventListener('mousedown', start);
  canvas.addEventListener('mousemove', move);
  window.addEventListener('mouseup', stop);
  canvas.addEventListener('touchstart', start);
  canvas.addEventListener('touchmove', move);
  canvas.addEventListener('touchend', stop);

  document.getElementById('palette').addEventListener('click', function (e) {
    const t = e.target.closest('.swatch');
    if (!t) return;
    document.querySelectorAll('#palette .swatch').forEach(s => s.classList.remove('active'));
    t.classList.add('active');
    color = t.dataset.color;
  });

  document.getElementById('brushes').addEventListener('click', function (e) {
    const t = e.target.closest('.brush');
    if (!t) return;
    document.querySelectorAll('#brushes .brush').forEach(s => s.classList.remove('active'));
    t.classList.add('active');
    size = parseInt(t.dataset.size, 10);
  });

  document.getElementById('clear-btn').addEventListener('click', function () {
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  });

  document.getElementById('save-form').addEventListener('submit', function () {
    document.getElementById('image-data').value = canvas.toDataURL('image/png');
  });
})();
