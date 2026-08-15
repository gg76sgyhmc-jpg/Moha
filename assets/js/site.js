/* ==========================================================================
   إعمار وإستثمار العقارية — سلوك الموقع
   لا اعتماديات خارجية. كل زر في الصفحة موصول من هنا.
   ========================================================================== */
(function () {
  'use strict';

  var WA_NUMBER = '966506833445';
  var $  = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------- إشعار صغير ---------- */
  var toastEl = $('#toast');
  var toastTx = $('#toast-text');
  var toastTimer = null;
  function toast(msg) {
    if (!toastEl || !toastTx) return;
    toastTx.textContent = msg;
    toastEl.classList.add('is-on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('is-on'); }, 2600);
  }

  /* ---------- السنة في التذييل ---------- */
  var yearEl = $('#year');
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  /* ---------- الشريط العلوي: ظل عند التمرير ---------- */
  var nav = $('#nav');
  var toTop = $('#totop');
  function onScroll() {
    var y = window.pageYOffset || document.documentElement.scrollTop;
    if (nav) nav.classList.toggle('is-stuck', y > 12);
    if (toTop) toTop.classList.toggle('is-on', y > 600);
    // في أعلى الصفحة لا يوجد قسم نشط — نزيل التمييز بدل إبقائه على آخر قسم
    if (y < 240) markActive('');
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if (toTop) {
    toTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: prefersReduced() ? 'auto' : 'smooth' });
    });
  }

  function prefersReduced() {
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  /* ---------- قائمة الجوال ---------- */
  var burger = $('#burger');
  var drawer = $('#drawer');
  function setDrawer(open) {
    if (!burger || !drawer) return;
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    burger.setAttribute('aria-label', open ? 'إغلاق القائمة' : 'فتح القائمة');
    drawer.classList.toggle('is-open', open);
  }
  if (burger && drawer) {
    burger.addEventListener('click', function () {
      setDrawer(burger.getAttribute('aria-expanded') !== 'true');
    });
    $$('a', drawer).forEach(function (a) {
      a.addEventListener('click', function () { setDrawer(false); });
    });
    document.addEventListener('click', function (e) {
      if (!drawer.classList.contains('is-open')) return;
      if (drawer.contains(e.target) || burger.contains(e.target)) return;
      setDrawer(false);
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 900) setDrawer(false);
    });
  }

  /* ---------- تتبّع القسم الحالي في القائمة ---------- */
  var navLinks = $$('.nav__links a');
  var sections = navLinks
    .map(function (a) {
      var id = a.getAttribute('href');
      return id && id.charAt(0) === '#' ? document.getElementById(id.slice(1)) : null;
    })
    .filter(Boolean);

  function markActive(id) {
    if (!navLinks) return;   /* قد تُستدعى من onScroll قبل تهيئة الروابط */
    navLinks.forEach(function (a) {
      var on = a.getAttribute('href') === '#' + id;
      if (on) a.setAttribute('aria-current', 'true');
      else a.removeAttribute('aria-current');
    });
  }

  if ('IntersectionObserver' in window && sections.length) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) markActive(en.target.id);
      });
    }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });
    sections.forEach(function (s) { spy.observe(s); });
  }

  /* ---------- ظهور تدريجي للأقسام ---------- */
  var rises = $$('.rise');
  if ('IntersectionObserver' in window && !prefersReduced()) {
    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('is-in');
        obs.unobserve(en.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
    rises.forEach(function (el, i) {
      el.style.transitionDelay = (Math.min(i % 6, 5) * 55) + 'ms';
      io.observe(el);
    });
  } else {
    rises.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* ---------- أزرار النسخ ---------- */
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try {
        var ok = document.execCommand('copy');
        document.body.removeChild(ta);
        ok ? resolve() : reject(new Error('copy failed'));
      } catch (err) {
        document.body.removeChild(ta);
        reject(err);
      }
    });
  }

  $$('[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var val = btn.getAttribute('data-copy');
      var msg = btn.getAttribute('data-copy-msg') || 'تم النسخ';
      copyText(val).then(
        function () {
          toast(msg);
          if (btn.classList.contains('copy-btn')) {
            btn.classList.add('is-done');
            setTimeout(function () { btn.classList.remove('is-done'); }, 2000);
          }
        },
        function () { toast('تعذّر النسخ — انسخه يدوياً: ' + val); }
      );
    });
  });

  /* ---------- مشاركة ---------- */
  var shareBtn = $('#share-btn');
  if (shareBtn) {
    shareBtn.addEventListener('click', function () {
      var data = {
        title: 'إعمار وإستثمار العقارية',
        text: 'مكتب إعمار وإستثمار العقارية — الخبر، حي الشراع.',
        url: window.location.href
      };
      if (navigator.share) {
        navigator.share(data).catch(function () { /* ألغى المستخدم المشاركة */ });
      } else {
        copyText(window.location.href).then(
          function () { toast('تم نسخ رابط الموقع'); },
          function () { toast('الرابط: ' + window.location.href); }
        );
      }
    });
  }

  /* ---------- مفتوح الآن / مغلق (بتوقيت الرياض) ---------- */
  var SLOTS = [[9 * 60, 12 * 60], [16 * 60, 22 * 60]];
  function riyadhMinutes() {
    try {
      var parts = new Intl.DateTimeFormat('en-US', {
        timeZone: 'Asia/Riyadh', hour: '2-digit', minute: '2-digit', hour12: false
      }).formatToParts(new Date());
      var h = 0, m = 0;
      parts.forEach(function (p) {
        if (p.type === 'hour') h = parseInt(p.value, 10);
        if (p.type === 'minute') m = parseInt(p.value, 10);
      });
      if (h === 24) h = 0;
      return h * 60 + m;
    } catch (e) {
      var d = new Date();
      return ((d.getUTCHours() + 3) % 24) * 60 + d.getUTCMinutes();
    }
  }
  function fmt(mins) {
    var h = Math.floor(mins / 60), m = mins % 60;
    return (h < 10 ? '0' : '') + h + ':' + (m < 10 ? '0' : '') + m;
  }
  function refreshStatus() {
    var box = $('#open-status');
    var txt = $('#open-text');
    if (!box || !txt) return;
    var now = riyadhMinutes();
    var openSlot = null, nextOpen = null;
    for (var i = 0; i < SLOTS.length; i++) {
      if (now >= SLOTS[i][0] && now < SLOTS[i][1]) { openSlot = SLOTS[i]; break; }
      if (now < SLOTS[i][0] && nextOpen === null) nextOpen = SLOTS[i][0];
    }
    box.classList.remove('status--open', 'status--shut');
    if (openSlot) {
      box.classList.add('status--open');
      txt.textContent = 'مفتوح الآن · حتى ' + fmt(openSlot[1]);
    } else {
      box.classList.add('status--shut');
      txt.textContent = nextOpen !== null
        ? 'مغلق · يفتح ' + fmt(nextOpen)
        : 'مغلق · يفتح غداً ' + fmt(SLOTS[0][0]);
    }
  }
  refreshStatus();
  setInterval(refreshStatus, 60000);

  /* ---------- عارض الصور ---------- */
  var lb      = $('#lightbox');
  var lbImg   = $('#lb-img');
  var lbCap   = $('#lb-cap');
  var lbCount = $('#lb-count');
  var shots   = $$('.shot');
  var idx = 0;
  var lastFocus = null;

  function showShot(i) {
    if (!shots.length) return;
    idx = (i + shots.length) % shots.length;
    var fig = shots[idx];
    var src = fig.getAttribute('data-src');
    var cap = fig.getAttribute('data-cap') || '';
    if (lbImg) { lbImg.setAttribute('src', src); lbImg.setAttribute('alt', cap); }
    if (lbCap) lbCap.textContent = cap;
    if (lbCount) lbCount.textContent = (idx + 1) + ' / ' + shots.length;
  }
  function openLb(i) {
    if (!lb) return;
    lastFocus = document.activeElement;
    showShot(i);
    lb.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    var x = $('#lb-close');
    if (x) x.focus();
  }
  function closeLb() {
    if (!lb) return;
    lb.classList.remove('is-open');
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  shots.forEach(function (fig, i) {
    fig.addEventListener('click', function () { openLb(i); });
    fig.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') {
        e.preventDefault();
        openLb(i);
      }
    });
  });

  var lbClose = $('#lb-close'), lbPrev = $('#lb-prev'), lbNext = $('#lb-next');
  if (lbClose) lbClose.addEventListener('click', closeLb);
  if (lbPrev)  lbPrev.addEventListener('click', function () { showShot(idx - 1); });
  if (lbNext)  lbNext.addEventListener('click', function () { showShot(idx + 1); });
  if (lb) {
    lb.addEventListener('click', function (e) {
      if (e.target === lb) closeLb();
    });
    // سحب بالإصبع
    var sx = 0, sy = 0;
    lb.addEventListener('touchstart', function (e) {
      sx = e.changedTouches[0].clientX; sy = e.changedTouches[0].clientY;
    }, { passive: true });
    lb.addEventListener('touchend', function (e) {
      var dx = e.changedTouches[0].clientX - sx;
      var dy = e.changedTouches[0].clientY - sy;
      if (Math.abs(dx) > 55 && Math.abs(dx) > Math.abs(dy)) {
        showShot(dx > 0 ? idx - 1 : idx + 1);   /* RTL: سحب لليمين = السابق */
      }
    }, { passive: true });
  }

  document.addEventListener('keydown', function (e) {
    if (lb && lb.classList.contains('is-open')) {
      if (e.key === 'Escape') { closeLb(); return; }
      if (e.key === 'ArrowLeft')  { showShot(idx + 1); return; }
      if (e.key === 'ArrowRight') { showShot(idx - 1); return; }
      if (e.key === 'Tab') {
        var focusables = [lbClose, lbPrev, lbNext].filter(Boolean);
        if (!focusables.length) return;
        var pos = focusables.indexOf(document.activeElement);
        e.preventDefault();
        var nextPos = e.shiftKey ? pos - 1 : pos + 1;
        if (nextPos < 0) nextPos = focusables.length - 1;
        if (nextPos >= focusables.length) nextPos = 0;
        focusables[nextPos].focus();
      }
      return;
    }
    if (e.key === 'Escape' && drawer && drawer.classList.contains('is-open')) setDrawer(false);
  });

  /* ---------- نموذج الطلب ← واتساب ---------- */
  var form = $('#lead-form');

  function setError(input, message) {
    var field = input.closest('.field');
    var slot = field ? $('.err', field) : null;
    if (field) field.classList.toggle('is-bad', !!message);
    if (slot) slot.textContent = message || '';
    if (message) input.setAttribute('aria-invalid', 'true');
    else input.removeAttribute('aria-invalid');
  }

  function normalisePhone(raw) {
    var d = String(raw).replace(/[^\d+]/g, '');
    d = d.replace(/^\+/, '');
    if (d.indexOf('00966') === 0) d = d.slice(5);
    else if (d.indexOf('966') === 0) d = d.slice(3);
    d = d.replace(/^0+/, '');
    return d;
  }
  function phoneValid(raw) {
    var d = normalisePhone(raw);
    return /^5\d{8}$/.test(d);
  }

  if (form) {
    var nameI  = $('#f-name');
    var phoneI = $('#f-phone');

    [nameI, phoneI].forEach(function (input) {
      if (!input) return;
      input.addEventListener('input', function () {
        if (input.getAttribute('aria-invalid') === 'true') setError(input, '');
      });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = true;

      if (!nameI.value.trim() || nameI.value.trim().length < 2) {
        setError(nameI, 'اكتب اسمك من فضلك.');
        ok = false;
      } else setError(nameI, '');

      if (!phoneI.value.trim()) {
        setError(phoneI, 'نحتاج رقم جوالك للتواصل معك.');
        ok = false;
      } else if (!phoneValid(phoneI.value)) {
        setError(phoneI, 'أدخل رقم جوال سعودي صحيح — مثال: 0501234567.');
        ok = false;
      } else setError(phoneI, '');

      if (!ok) {
        var bad = $('.field.is-bad input', form);
        if (bad) bad.focus();
        return;
      }

      var lines = [
        'السلام عليكم،',
        '',
        'الاسم: ' + nameI.value.trim(),
        'الجوال: 0' + normalisePhone(phoneI.value),
        'نوع الطلب: ' + $('#f-intent').value,
        'نوع العقار: ' + $('#f-type').value
      ];
      var area = $('#f-area').value.trim();
      if (area) lines.push('الحي / المخطط: ' + area);
      var msg = $('#f-msg').value.trim();
      if (msg) { lines.push('', 'التفاصيل:', msg); }
      lines.push('', '— مُرسلة من موقع إعمار وإستثمار العقارية');

      var url = 'https://wa.me/' + WA_NUMBER + '?text=' + encodeURIComponent(lines.join('\n'));
      var win = window.open(url, '_blank', 'noopener');
      if (win) {
        toast('فتحنا لك محادثة واتساب — اضغط إرسال.');
      } else {
        copyText(lines.join('\n')).then(
          function () { toast('تم نسخ الرسالة — الصقها في واتساب على 0506833445.'); },
          function () { window.location.href = url; }
        );
      }
    });
  }
})();
