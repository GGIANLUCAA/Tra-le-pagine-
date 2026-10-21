(() => {
  if (typeof draw !== 'function' || typeof filtered !== 'function') return;
  const style = document.createElement('style'); style.textContent = '.poster img{object-fit:contain;background:#080e18}.poster .badge,.poster .duration,.poster .heart{z-index:2}'; document.head.append(style);
  const images = new Map(), jobs = [], queued = new Set();
  let running = false;
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) if (entry.isIntersecting) {
      observer.unobserve(entry.target);
      const {previewKey:key, previewSize:size} = entry.target.dataset;
      const id = key + ':' + size;
      if (images.has(id)) paint(entry.target, images.get(id));
      else if (!queued.has(id)) { queued.add(id); jobs.push({key, size, id}); pump(); }
    }
  }, {rootMargin:'160px'});
  function paint(node, url) {
    if (!node.isConnected || node.querySelector('img')) return;
    const img = new Image(); img.alt = 'Anteprima del video'; img.decoding = 'async';
    img.src = url; img.dataset.generatedPreview = 'true'; node.append(img);
  }
  function capture(key) {
    return new Promise((resolve, reject) => {
      const video = document.createElement('video');
      video.muted = true; video.playsInline = true; video.preload = 'auto';
      let finished = false;
      const timer = setTimeout(() => finish(new Error('Preview timeout')), 20000);
      function finish(err, blob) {
        if (finished) return; finished = true; clearTimeout(timer);
        video.pause(); video.removeAttribute('src'); video.load();
        if (err) reject(err); else resolve(URL.createObjectURL(blob));
      }
      video.onerror = () => finish(new Error('Video unavailable'));
      video.onloadedmetadata = () => {
        video.currentTime = Math.min(2, Number.isFinite(video.duration) ? Math.max(.01, video.duration * .15) : 1);
      };
      video.onseeked = () => {
        if (!video.videoWidth || !video.videoHeight) return finish(new Error('Empty frame'));
        const canvas = document.createElement('canvas');
        canvas.width = Math.min(640, video.videoWidth);
        canvas.height = Math.round(canvas.width * video.videoHeight / video.videoWidth);
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(blob => blob ? finish(null, blob) : finish(new Error('Empty thumbnail')), 'image/jpeg', .82);
      };
      video.src = '/media/' + encodeURIComponent(key); video.load();
    });
  }
  async function pump() {
    if (running) return; running = true;
    while (jobs.length) {
      const job = jobs.shift();
      if (![...document.querySelectorAll('[data-preview-key]')].some(n => n.dataset.previewKey === job.key && !n.querySelector('img'))) { queued.delete(job.id); continue; }
      try {
        const url = await capture(job.key); images.set(job.id, url);
        for (const node of document.querySelectorAll('[data-preview-key]')) if (node.dataset.previewKey === job.key) paint(node, url);
      } catch { queued.delete(job.id); }
    }
    running = false;
  }
  const originalDraw = draw;
  draw = function() {
    observer.disconnect(); originalDraw();
    const rows = filtered(), cards = document.querySelectorAll('#grid .card');
    cards.forEach((card, i) => {
      const x = rows[i], node = card.querySelector('.poster');
      if (!x || !node || x.available === false) return;
      node.dataset.previewKey = x.key; node.dataset.previewSize = x.size;
      const fallback = () => { if (!node.querySelector('img')) observer.observe(node); };
      const img = node.querySelector('img');
      if (img) { img.addEventListener('error', () => { img.remove(); fallback(); }, {once:true}); if (img.complete && !img.naturalWidth) {img.remove(); fallback();} }
      else fallback();
    });
  };
  draw();
  setInterval(() => { if (!document.hidden && typeof load === 'function') load(true); }, 60000);
})();
