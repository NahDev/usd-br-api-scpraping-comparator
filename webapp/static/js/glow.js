(function () {
  const glow = document.createElement('div');
  glow.className = 'cursor-glow';
  document.body.prepend(glow);

  let raf = null;
  window.addEventListener('mousemove', (e) => {
    if (raf) return;
    raf = requestAnimationFrame(() => {
      glow.style.setProperty('--mx', e.clientX + 'px');
      glow.style.setProperty('--my', e.clientY + 'px');
      raf = null;
    });
  });
})();
