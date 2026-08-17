/* ============================================================
   مكتب عقار اليوم للعقارات — سلوك الواجهة
   ============================================================ */
(function () {
  'use strict';

  var root = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
  var AR = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];

  function toArabic(str) {
    return String(str).replace(/[0-9]/g, function (d) { return AR[+d]; }).replace('.', '٫');
  }
  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function on(el, ev, fn, opt) { if (el) el.addEventListener(ev, fn, opt || false); }

  /* ---------- 1. شاشة الافتتاح ---------- */
  var loader = $('#loader');
  function hideLoader() {
    if (!loader || loader.classList.contains('is-done')) return;
    loader.classList.add('is-done');
    window.setTimeout(function () { loader.remove(); }, 800);
  }
  if (reduce.matches) { hideLoader(); }
  else {
    window.setTimeout(hideLoader, 1750);
    on(window, 'load', function () { window.setTimeout(hideLoader, 900); });
  }

  /* ---------- 2. مظهر الموقع ---------- */
  var modeBtn = $('#modeBtn');
  var saved = null;
  try { saved = localStorage.getItem('aqar-mode'); } catch (e) { /* الوضع الخاص */ }
  if (saved === 'day') { root.setAttribute('data-mode', 'day'); }

  function syncMode() {
    var day = root.getAttribute('data-mode') === 'day';
    if (modeBtn) {
      modeBtn.setAttribute('aria-pressed', day ? 'true' : 'false');
      modeBtn.setAttribute('aria-label', day ? 'التحويل إلى المظهر الليلي' : 'التحويل إلى المظهر النهاري');
    }
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', day ? '#F7F3EA' : '#070530');
  }
  syncMode();

  on(modeBtn, 'click', function () {
    var day = root.getAttribute('data-mode') === 'day';
    if (day) { root.removeAttribute('data-mode'); } else { root.setAttribute('data-mode', 'day'); }
    try { localStorage.setItem('aqar-mode', day ? 'night' : 'day'); } catch (e) { /* تجاهل */ }
    syncMode();
  });

  /* ---------- 3. الشريط العلوي وخيط التقدم ---------- */
  var nav = $('#nav');
  var threadFill = $('#threadFill');
  var fab = $('.fab');
  var toTop = $('#toTop');
  var sections = $$('main section[id]');
  var navLinks = $$('.nlink');
  var heroIn = $('.hero__in');
  var ticking = false;

  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    var max = document.documentElement.scrollHeight - window.innerHeight;

    if (nav) nav.classList.toggle('is-stuck', y > 24);
    if (threadFill) threadFill.style.width = (max > 0 ? (y / max) * 100 : 0) + '%';
    if (fab) fab.classList.toggle('is-in', y > 380);
    if (toTop) toTop.classList.toggle('is-in', y > 900);

    /* انزلاق لطيف لمحتوى الواجهة مع التمرير */
    if (heroIn && !reduce.matches) {
      var vh = window.innerHeight;
      if (y < vh) {
        var k = y / vh;
        heroIn.style.transform = 'translate3d(0,' + (k * 46).toFixed(1) + 'px,0)';
        heroIn.style.opacity = (1 - k * 0.85).toFixed(3);
      } else if (heroIn.style.opacity !== '0') {
        heroIn.style.opacity = '0';
      }
    }

    var current = '';
    var probe = y + window.innerHeight * 0.32;
    for (var i = 0; i < sections.length; i++) {
      if (sections[i].offsetTop <= probe) current = sections[i].id;
    }
    for (var j = 0; j < navLinks.length; j++) {
      navLinks[j].classList.toggle('is-on', navLinks[j].getAttribute('href') === '#' + current);
    }
    ticking = false;
  }
  on(window, 'scroll', function () {
    if (!ticking) { ticking = true; window.requestAnimationFrame(onScroll); }
  }, { passive: true });
  onScroll();

  on(toTop, 'click', function () {
    window.scrollTo({ top: 0, behavior: reduce.matches ? 'auto' : 'smooth' });
  });

  /* ---------- 4. قائمة الجوال ---------- */
  var drawer = $('#drawer');
  var menuBtn = $('#menuBtn');
  var drawerX = $('#drawerX');
  var drawerLinks = $$('.drawer__nav a');
  drawerLinks.forEach(function (a, i) { a.style.animationDelay = (90 + i * 55) + 'ms'; });

  function openDrawer() {
    if (!drawer) return;
    drawer.hidden = false;
    window.requestAnimationFrame(function () { drawer.classList.add('is-open'); });
    document.body.classList.add('is-locked');
    if (menuBtn) menuBtn.setAttribute('aria-expanded', 'true');
    window.setTimeout(function () { if (drawerX) drawerX.focus(); }, 260);
  }
  function closeDrawer() {
    if (!drawer || drawer.hidden) return;
    drawer.classList.remove('is-open');
    document.body.classList.remove('is-locked');
    if (menuBtn) { menuBtn.setAttribute('aria-expanded', 'false'); menuBtn.focus(); }
    window.setTimeout(function () { drawer.hidden = true; }, 520);
  }
  on(menuBtn, 'click', openDrawer);
  on(drawerX, 'click', closeDrawer);
  on(drawer, 'click', function (e) { if (e.target === drawer) closeDrawer(); });
  drawerLinks.forEach(function (a) { on(a, 'click', closeDrawer); });
  on(document, 'keydown', function (e) {
    if (e.key !== 'Escape' || !drawer || drawer.hidden) return;
    closeDrawer();
  });
  /* حصر التنقل بلوحة المفاتيح داخل القائمة */
  on(drawer, 'keydown', function (e) {
    if (e.key !== 'Tab' || drawer.hidden) return;
    var f = $$('a[href], button:not([disabled])', drawer);
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });

  /* ---------- 5. الكشف عند التمرير ---------- */
  var revealables = $$('.reveal');
  revealables.forEach(function (el) { el.style.setProperty('--d', el.dataset.rv || 0); });

  if (!('IntersectionObserver' in window) || reduce.matches) {
    revealables.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('is-in');
        io.unobserve(en.target);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.12 });
    revealables.forEach(function (el) { io.observe(el); });
  }

  /* ---------- 6. عدّادات الأرقام ---------- */
  var counters = $$('[data-count]');
  function runCounter(el) {
    var target = parseFloat(el.dataset.count);
    var dec = el.dataset.dec ? parseInt(el.dataset.dec, 10) : 0;
    var suffix = el.dataset.suffix || '';
    var plain = el.dataset.plain === '1';
    var dur = 1500;
    var t0 = performance.now();

    function frame(now) {
      var p = Math.min((now - t0) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 4);
      var val = target * eased;
      var out = plain ? String(Math.round(val)) : val.toFixed(dec);
      if (!plain && dec === 0) out = Number(out).toLocaleString('en-US');
      el.textContent = toArabic(out) + (p === 1 ? suffix : '');
      if (p < 1) window.requestAnimationFrame(frame);
    }
    window.requestAnimationFrame(frame);
  }

  if ('IntersectionObserver' in window && !reduce.matches) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        runCounter(en.target);
        cio.unobserve(en.target);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { cio.observe(el); });
  }

  /* ---------- 7. توهّج البطاقات وميلانها ---------- */
  var tilts = $$('.tilt, .card');
  tilts.forEach(function (el) {
    on(el, 'pointermove', function (e) {
      var r = el.getBoundingClientRect();
      var x = e.clientX - r.left, y = e.clientY - r.top;
      el.style.setProperty('--mx', x + 'px');
      el.style.setProperty('--my', y + 'px');
      if (!finePointer.matches || reduce.matches) return;
      if (!el.classList.contains('tilt') || !el.classList.contains('is-in')) return;
      var rx = ((y / r.height) - 0.5) * -5;
      var ry = ((x / r.width) - 0.5) * 5;
      el.style.transform = 'perspective(900px) rotateX(' + rx + 'deg) rotateY(' + ry + 'deg) translateY(-6px)';
    });
    on(el, 'pointerleave', function () { el.style.transform = ''; });
  });

  /* ---------- 8. الأزرار المغناطيسية ---------- */
  if (finePointer.matches && !reduce.matches) {
    $$('.magnet').forEach(function (el) {
      on(el, 'pointermove', function (e) {
        var r = el.getBoundingClientRect();
        var dx = (e.clientX - (r.left + r.width / 2)) * 0.16;
        var dy = (e.clientY - (r.top + r.height / 2)) * 0.28;
        el.style.transform = 'translate(' + dx + 'px,' + dy + 'px)';
      });
      on(el, 'pointerleave', function () { el.style.transform = ''; });
    });
  }

  /* ---------- 9. أثر اللمس ---------- */
  function ripple(e) {
    var el = e.currentTarget;
    var r = el.getBoundingClientRect();
    var size = Math.max(r.width, r.height) * 2.1;
    var span = document.createElement('span');
    span.className = 'ripple';
    span.style.width = span.style.height = size + 'px';
    span.style.left = (e.clientX - r.left) + 'px';
    span.style.top = (e.clientY - r.top) + 'px';
    el.appendChild(span);
    window.setTimeout(function () { span.remove(); }, 640);
  }
  if (!reduce.matches) {
    $$('.btn, .chip').forEach(function (el) { on(el, 'pointerdown', ripple); });
  }

  /* ---------- 10. نسخ الأرقام ---------- */
  var toast = $('#toast');
  var toastTimer = null;
  function say(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('is-in');
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(function () { toast.classList.remove('is-in'); }, 2100);
  }
  $$('[data-copy]').forEach(function (btn) {
    on(btn, 'click', function () {
      var val = btn.dataset.copy;
      var done = function () { say('تم نسخ الرقم: ' + val); };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(val).then(done, function () { say('الرقم: ' + val); });
      } else { say('الرقم: ' + val); }
    });
  });

  /* ---------- 11. السنة ---------- */
  var yearEl = $('#year');
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  /* ---------- 12. شبكة المعينات المتحركة في الواجهة ---------- */
  var canvas = $('#lattice');
  if (canvas && canvas.getContext) {
    var ctx = canvas.getContext('2d');
    var W = 0, H = 0, dpr = 1;
    var nodes = [];
    var ripples = [];
    var pointer = { x: -9999, y: -9999, tx: -9999, ty: -9999, on: false };
    var t = 0;
    var raf = null;
    var visible = true;

    function accent() {
      var v = getComputedStyle(root).getPropertyValue('--accent').trim();
      return v || '#D9BA7B';
    }
    function hexToRgb(h) {
      h = h.replace('#', '');
      if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
      var n = parseInt(h, 16);
      return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
    }
    var rgb = hexToRgb(accent());

    function build() {
      var rect = canvas.getBoundingClientRect();
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = rect.width; H = rect.height;
      canvas.width = Math.round(W * dpr);
      canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      var step = W < 620 ? 74 : W < 1100 ? 92 : 108;
      nodes = [];
      for (var y = -step; y < H + step; y += step) {
        var row = Math.round(y / step);
        for (var x = -step; x < W + step * 2; x += step) {
          nodes.push({
            x: x + (row % 2 ? step / 2 : 0),
            y: y,
            p: Math.random() * Math.PI * 2,
            s: 0.55 + Math.random() * 0.55
          });
        }
      }
      rgb = hexToRgb(accent());
    }

    function diamond(x, y, r, a, lw) {
      ctx.beginPath();
      ctx.moveTo(x, y - r);
      ctx.lineTo(x + r, y);
      ctx.lineTo(x, y + r);
      ctx.lineTo(x - r, y);
      ctx.closePath();
      ctx.strokeStyle = 'rgba(' + rgb[0] + ',' + rgb[1] + ',' + rgb[2] + ',' + a.toFixed(3) + ')';
      ctx.lineWidth = lw;
      ctx.stroke();
    }

    function draw(now) {
      raf = null;
      if (!visible) return;
      t = now || 0;
      ctx.clearRect(0, 0, W, H);
      ctx.lineJoin = 'round';
      ctx.lineCap = 'round';

      pointer.x += (pointer.tx - pointer.x) * 0.07;
      pointer.y += (pointer.ty - pointer.y) * 0.07;

      var sweep = ((t * 0.045) % (W + H + 600)) - 300;
      var px = (pointer.x - W / 2) * 0.014;
      var py = (pointer.y - H / 2) * 0.014;

      for (var i = 0; i < nodes.length; i++) {
        var n = nodes[i];
        var x = n.x - px, y = n.y - py;
        var breathe = Math.sin(t * 0.0009 + n.p) * 0.5 + 0.5;
        var base = 8 + breathe * 7 * n.s;
        var alpha = 0.05 + breathe * 0.09;

        /* موجة الضوء المائلة */
        var d = Math.abs((x + y) - sweep);
        if (d < 260) { var w = 1 - d / 260; alpha += w * w * 0.3; base += w * w * 7; }

        /* تأثير المؤشر أو اللمس */
        if (pointer.on) {
          var dx = x - pointer.x, dy = y - pointer.y;
          var dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 230) { var f = 1 - dist / 230; alpha += f * f * 0.42; base += f * f * 13; }
        }

        /* حلقات اللمس */
        for (var k = 0; k < ripples.length; k++) {
          var rp = ripples[k];
          var ddx = x - rp.x, ddy = y - rp.y;
          var dd = Math.sqrt(ddx * ddx + ddy * ddy);
          var band = Math.abs(dd - rp.r);
          if (band < 78) {
            var g = (1 - band / 78) * rp.life;
            alpha += g * 0.55; base += g * 16;
          }
        }

        diamond(x, y, base, Math.min(alpha, 0.72), alpha > 0.28 ? 1.25 : 0.85);
      }

      for (var m = ripples.length - 1; m >= 0; m--) {
        ripples[m].r += 8.5;
        ripples[m].life -= 0.014;
        if (ripples[m].life <= 0) ripples.splice(m, 1);
      }

      raf = window.requestAnimationFrame(draw);
    }

    function start() { if (!raf && !reduce.matches) raf = window.requestAnimationFrame(draw); }
    function stop() { if (raf) { window.cancelAnimationFrame(raf); raf = null; } }

    build();
    if (reduce.matches) {
      /* لقطة ثابتة واحدة عند تفضيل تقليل الحركة */
      ctx.lineJoin = 'round';
      nodes.forEach(function (n) { diamond(n.x, n.y, 11, 0.13, 1); });
    } else { start(); }

    var rsz = null;
    on(window, 'resize', function () {
      window.clearTimeout(rsz);
      rsz = window.setTimeout(function () {
        build();
        if (reduce.matches) { ctx.clearRect(0, 0, W, H); nodes.forEach(function (n) { diamond(n.x, n.y, 11, 0.13, 1); }); }
      }, 180);
    }, { passive: true });

    on(canvas.parentElement, 'pointermove', function (e) {
      var r = canvas.getBoundingClientRect();
      pointer.tx = e.clientX - r.left; pointer.ty = e.clientY - r.top; pointer.on = true;
    }, { passive: true });
    on(canvas.parentElement, 'pointerleave', function () { pointer.on = false; });
    on(canvas.parentElement, 'pointerdown', function (e) {
      var r = canvas.getBoundingClientRect();
      var x = e.clientX - r.left, y = e.clientY - r.top;
      pointer.tx = x; pointer.ty = y; pointer.on = true;
      if (ripples.length < 6) ripples.push({ x: x, y: y, r: 12, life: 1 });
    }, { passive: true });

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) {
        visible = en[0].isIntersecting;
        if (visible) start(); else stop();
      }, { threshold: 0.02 }).observe(canvas);
    }
    on(document, 'visibilitychange', function () {
      if (document.hidden) stop(); else if (visible) start();
    });
    /* تحديث لون الشبكة عند تبديل المظهر */
    on(modeBtn, 'click', function () { window.setTimeout(function () { rgb = hexToRgb(accent()); }, 60); });
  }
})();
