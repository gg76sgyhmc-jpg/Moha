/* ==========================================================================
   مكتب لوامع للعقارات — التفاعلات والحركة
   بدون أي مكتبات خارجية · يحترم prefers-reduced-motion
   ========================================================================== */
(function () {
  'use strict';

  var CFG = window.SITE_CONFIG || {};
  var root = document.documentElement;
  var $  = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };
  var lerp = function (a, b, t) { return a + (b - a) * t; };

  /* ══════════════════════════════════════════════════════════════
     1) الوضع الليلي / النهاري
     ══════════════════════════════════════════════════════════════ */
  (function theme() {
    var KEY = 'lawamea-theme';
    var btn = $('#themeToggle');
    var stored = null;
    try { stored = localStorage.getItem(KEY); } catch (e) {}

    var mq = window.matchMedia('(prefers-color-scheme: dark)');
    var current = stored || (mq.matches ? 'dark' : 'light');

    function apply(mode, persist) {
      current = mode;
      root.setAttribute('data-theme', mode);
      if (btn) btn.setAttribute('aria-pressed', String(mode === 'dark'));
      if (persist) { try { localStorage.setItem(KEY, mode); } catch (e) {} }
    }

    apply(current, false);

    mq.addEventListener && mq.addEventListener('change', function (e) {
      if (!stored) apply(e.matches ? 'dark' : 'light', false);
    });

    if (btn) btn.addEventListener('click', function () {
      stored = current === 'dark' ? 'light' : 'dark';
      apply(stored, true);
    });
  })();

  /* ══════════════════════════════════════════════════════════════
     2) ربط روابط التواصل من ملف الإعدادات
     ══════════════════════════════════════════════════════════════ */
  var LINKS = (function links() {
    var phone = (CFG.phone || '').replace(/[^\d]/g, '');
    var tel = phone ? 'tel:+' + phone : '';
    var waBase = phone ? 'https://wa.me/' + phone : '';
    var maps = CFG.maps || '';
    var s = CFG.social || {};

    function wa(text) {
      if (!waBase) return '#';
      var t = text || CFG.waDefault || '';
      return waBase + (t ? '?text=' + encodeURIComponent(t) : '');
    }

    $$('[data-tel-href]').forEach(function (a) {
      if (tel) { a.href = tel; } else { a.removeAttribute('href'); }
    });

    $$('[data-wa]').forEach(function (a) {
      a.href = wa(a.getAttribute('data-wa'));
      a.target = '_blank';
      a.rel = 'noopener';
    });

    $$('[data-link="maps"]').forEach(function (a) { if (maps) a.href = maps; });
    $$('[data-link="haraj"]').forEach(function (a) {
      if (s.haraj) { a.href = s.haraj; } else { a.hidden = true; }
    });

    /* أيقونات التواصل الاجتماعي — تُبنى فقط لما هو معبّأ في config.js */
    var ICONS = {
      whatsapp: { label: 'واتساب',   d: 'M12.04 2C6.6 2 2.2 6.4 2.2 11.85c0 1.9.5 3.7 1.4 5.3L2 22.5l5.5-1.45a9.9 9.9 0 0 0 4.54 1.1h.01c5.44 0 9.85-4.4 9.85-9.85C21.9 6.4 17.48 2 12.04 2Zm5.75 14.02c-.24.68-1.4 1.3-1.94 1.35-.5.05-.98.23-3.3-.7-2.77-1.1-4.53-3.94-4.67-4.12-.13-.19-1.11-1.48-1.11-2.83 0-1.34.7-2 .95-2.28.25-.27.55-.34.73-.34h.53c.17 0 .4-.06.63.48.23.55.79 1.9.86 2.04.07.13.11.29.02.47-.09.18-.13.29-.27.45-.13.15-.28.34-.4.46-.14.13-.28.28-.12.55.16.27.71 1.17 1.53 1.9 1.05.93 1.94 1.22 2.21 1.36.27.13.43.11.59-.07.16-.18.68-.79.86-1.06.18-.27.36-.22.6-.13.25.09 1.58.74 1.85.88.27.13.45.2.52.31.07.11.07.63-.17 1.31Z' },
      x:        { label: 'منصة إكس', d: 'M17.53 3h3.06l-6.69 7.64L21.75 21h-6.16l-4.83-6.3L5.24 21H2.18l7.15-8.17L2.5 3h6.32l4.36 5.77L17.53 3Zm-1.07 16.17h1.7L7.62 4.74H5.8l10.66 14.43Z' },
      instagram:{ label: 'إنستقرام', d: 'M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23a3.7 3.7 0 0 1-.9 1.38c-.42.42-.82.68-1.38.9-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41a3.7 3.7 0 0 1-1.38-.9 3.7 3.7 0 0 1-.9-1.38c-.16-.42-.36-1.06-.41-2.23-.06-1.27-.07-1.65-.07-4.85s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41 1.27-.06 1.65-.07 4.85-.07ZM12 7.83a4.17 4.17 0 1 0 0 8.34 4.17 4.17 0 0 0 0-8.34Zm0 6.88a2.71 2.71 0 1 1 0-5.42 2.71 2.71 0 0 1 0 5.42Zm5.31-7.04a.97.97 0 1 1-1.95 0 .97.97 0 0 1 1.95 0Z' },
      snapchat: { label: 'سناب شات', d: 'M12.02 2.2c2.53.02 4.4 1.86 4.55 4.4.05.86.02 1.73.02 2.6 0 .2.05.28.26.29.35.02.72-.02 1.05.07.66.18.85.85.4 1.36-.28.32-.66.5-1.04.66-.35.15-.7.28-1.03.46-.33.18-.4.4-.25.75.85 1.94 2.27 3.15 4.33 3.63.5.12.6.35.4.83-.2.5-.62.7-1.1.83-.5.13-1.02.2-1.53.26-.24.03-.34.13-.4.36-.06.24-.12.48-.2.72-.13.4-.34.5-.75.42a7.4 7.4 0 0 0-2.1-.14c-.75.07-1.36.44-1.93.9-1.32 1.06-3.14 1.06-4.47.02-.7-.55-1.44-.94-2.36-.94-.55 0-1.1.07-1.65.16-.42.07-.63-.03-.76-.44l-.2-.7c-.07-.26-.2-.36-.46-.4-.53-.06-1.06-.13-1.57-.28-.44-.13-.83-.34-1.02-.8-.2-.48-.1-.72.4-.84 2.07-.5 3.5-1.7 4.35-3.65.14-.33.07-.55-.25-.72-.3-.16-.62-.3-.94-.43-.4-.17-.8-.35-1.1-.68-.47-.5-.28-1.2.4-1.38.34-.1.72-.05 1.08-.07.2-.01.24-.1.24-.28 0-.9-.03-1.8.03-2.7.16-2.5 2.03-4.3 4.53-4.32Z' },
      tiktok:   { label: 'تيك توك',  d: 'M16.6 5.82a4.28 4.28 0 0 1-1.06-2.82h-3.1v12.4a2.6 2.6 0 0 1-2.6 2.5 2.6 2.6 0 0 1 0-5.2c.27 0 .53.05.78.12v-3.2a5.8 5.8 0 0 0-.78-.05 5.72 5.72 0 1 0 5.72 5.72V9.42a7.36 7.36 0 0 0 4.3 1.38V7.7a4.3 4.3 0 0 1-3.26-1.88Z' },
      youtube:  { label: 'يوتيوب',   d: 'M21.6 7.2a2.5 2.5 0 0 0-1.76-1.77C18.26 5 12 5 12 5s-6.26 0-7.84.43A2.5 2.5 0 0 0 2.4 7.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.76 1.77C5.74 19 12 19 12 19s6.26 0 7.84-.43a2.5 2.5 0 0 0 1.76-1.77A26 26 0 0 0 22 12a26 26 0 0 0-.4-4.8ZM10 15.1V8.9l5.2 3.1-5.2 3.1Z' },
      maps:     { label: 'خرائط قوقل', d: 'M12 2a7 7 0 0 0-7 7c0 5.1 7 13 7 13s7-7.9 7-13a7 7 0 0 0-7-7Zm0 9.6A2.6 2.6 0 1 1 12 6.4a2.6 2.6 0 0 1 0 5.2Z' },
      haraj:    { label: 'حراج',      d: 'M4 4h7v7H4V4Zm9 0h7v7h-7V4ZM4 13h7v7H4v-7Zm9 0h7v7h-7v-7Z' },
      email:    { label: 'البريد',    d: 'M3 5.5h18c.55 0 1 .45 1 1v11c0 .55-.45 1-1 1H3c-.55 0-1-.45-1-1v-11c0-.55.45-1 1-1Zm1.6 2L12 12.6l7.4-5.1H4.6Z' }
    };

    var ORDER = ['whatsapp', 'x', 'instagram', 'snapchat', 'tiktok', 'youtube', 'maps', 'haraj', 'email'];

    function resolve(key) {
      var v = s[key];
      if (v === 'auto') {
        if (key === 'whatsapp') return waBase ? wa(null) : '';
        if (key === 'maps') return maps;
        return '';
      }
      if (!v) return '';
      if (key === 'email') return 'mailto:' + v;
      return v;
    }

    function build(target) {
      if (!target) return;
      var frag = document.createDocumentFragment();
      ORDER.forEach(function (key) {
        var url = resolve(key);
        if (!url || !ICONS[key]) return;
        var li = document.createElement('li');
        var a = document.createElement('a');
        a.href = url;
        a.setAttribute('aria-label', ICONS[key].label);
        a.title = ICONS[key].label;
        if (key !== 'email') { a.target = '_blank'; a.rel = 'noopener'; }
        a.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="' + ICONS[key].d + '"/></svg>';
        li.appendChild(a);
        frag.appendChild(li);
      });
      target.appendChild(frag);
    }

    build($('#socialList'));
    build($('#socialListFooter'));

    return { wa: wa, tel: tel, maps: maps };
  })();

  /* ══════════════════════════════════════════════════════════════
     3) ستارة التحميل
     ══════════════════════════════════════════════════════════════ */
  (function preloader() {
    var el = $('#preloader');
    if (!el) return;
    var done = false;
    function hide() {
      if (done) return;
      done = true;
      el.classList.add('is-done');
      document.body.classList.add('is-ready');
      setTimeout(function () { el.remove(); }, 700);
      $$('.gleam-host').forEach(function (h, i) {
        setTimeout(function () {
          h.classList.add('is-gleaming');
          setTimeout(function () { h.classList.remove('is-gleaming'); }, 1300);
        }, 250 + i * 180);
      });
    }
    if (reduced.matches) { hide(); return; }
    window.addEventListener('load', function () { setTimeout(hide, 260); });
    setTimeout(hide, 2200);
  })();

  /* ══════════════════════════════════════════════════════════════
     4) الهيدر + شريط التقدّم
     ══════════════════════════════════════════════════════════════ */
  (function header() {
    var head = $('#header');
    var prog = $('#scrollProgress');
    var bar = prog ? prog.firstElementChild : null;
    var dock = $('#dock');
    var last = 0, ticking = false;

    function update() {
      var y = window.scrollY || window.pageYOffset;
      var max = document.documentElement.scrollHeight - window.innerHeight;

      if (head) {
        head.classList.toggle('is-stuck', y > 12);
        // إخفاء الهيدر عند النزول السريع، وإظهاره فوراً عند الصعود
        if (y > 320 && y > last + 6 && !document.body.classList.contains('is-locked')) {
          head.classList.add('is-hidden');
        } else if (y < last - 4 || y < 320) {
          head.classList.remove('is-hidden');
        }
      }

      if (bar) bar.style.transform = 'scaleX(' + (max > 0 ? clamp(y / max, 0, 1) : 0) + ')';
      if (dock) dock.classList.toggle('is-visible', y > 420);

      last = y;
      ticking = false;
    }

    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    update();
  })();

  /* ══════════════════════════════════════════════════════════════
     5) التنقل — الحبّة المتحركة + التمييز حسب القسم
     ══════════════════════════════════════════════════════════════ */
  (function nav() {
    var nav = $('#nav');
    if (!nav) return;
    var pill = $('.nav__pill', nav);
    var links = $$('.nav__list a', nav);
    var active = null;

    function move(el) {
      if (!el || !pill) return;
      var nr = nav.getBoundingClientRect();
      var r = el.getBoundingClientRect();
      pill.style.width = r.width + 'px';
      pill.style.transform = 'translateX(' + (r.left - nr.left) + 'px)';
      nav.classList.add('is-tracking');
    }
    function reset() {
      if (active) { move(active); }
      else { nav.classList.remove('is-tracking'); }
    }

    links.forEach(function (a) {
      a.addEventListener('mouseenter', function () { move(a); });
      a.addEventListener('focus', function () { move(a); });
    });
    nav.addEventListener('mouseleave', reset);
    window.addEventListener('resize', reset);

    var sections = links.map(function (a) { return $(a.getAttribute('href')); }).filter(Boolean);
    if (!sections.length) return;

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var id = '#' + e.target.id;
        links.forEach(function (a) {
          var on = a.getAttribute('href') === id;
          a.classList.toggle('is-active', on);
          if (on) active = a;
        });
        reset();
      });
    }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });

    sections.forEach(function (s) { io.observe(s); });
  })();

  /* ══════════════════════════════════════════════════════════════
     6) قائمة الجوال
     ══════════════════════════════════════════════════════════════ */
  (function menu() {
    var burger = $('#burger');
    var menu = $('#mobileMenu');
    if (!burger || !menu) return;
    var open = false;
    var lastFocus = null;

    function setOpen(v) {
      open = v;
      burger.setAttribute('aria-expanded', String(v));
      burger.setAttribute('aria-label', v ? 'إغلاق القائمة' : 'فتح القائمة');
      document.body.classList.toggle('is-locked', v);

      if (v) {
        lastFocus = document.activeElement;
        menu.hidden = false;
        requestAnimationFrame(function () { menu.classList.add('is-open'); });
        var first = $('.menu__list a', menu);
        if (first) setTimeout(function () { first.focus({ preventScroll: true }); }, 260);
      } else {
        menu.classList.remove('is-open');
        setTimeout(function () { if (!open) menu.hidden = true; }, 420);
        if (lastFocus) lastFocus.focus({ preventScroll: true });
      }
    }

    burger.addEventListener('click', function () { setOpen(!open); });
    $$('a', menu).forEach(function (a) { a.addEventListener('click', function () { setOpen(false); }); });
    $('.menu__bg', menu).addEventListener('click', function () { setOpen(false); });

    document.addEventListener('keydown', function (e) {
      if (!open) return;
      if (e.key === 'Escape') { setOpen(false); return; }
      if (e.key !== 'Tab') return;
      var f = $$('a, button', menu).filter(function (el) { return el.offsetParent !== null; });
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });

    window.addEventListener('resize', function () { if (open && window.innerWidth >= 980) setOpen(false); });
  })();

  /* ══════════════════════════════════════════════════════════════
     7) الكشف بالتمرير
     ══════════════════════════════════════════════════════════════ */
  (function reveal() {
    var items = $$('[data-reveal]');
    if (!items.length) return;

    items.forEach(function (el) {
      var d = parseInt(el.getAttribute('data-delay') || '0', 10);
      if (d) el.style.setProperty('--rd', (d * 95) + 'ms');
    });

    if (reduced.matches || !('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }

    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('is-in');
        obs.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });

    items.forEach(function (el) { io.observe(el); });

    /* بطاقات السكة قد تكون خارج الشاشة أفقياً فلا يلاحظها المراقب؛
       لذلك تُكشف جميعها بمجرد ظهور السكة نفسها. */
    $$('[data-rail]').forEach(function (railEl) {
      var rio = new IntersectionObserver(function (entries, obs) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          $$('[data-reveal]', railEl).forEach(function (el, i) {
            if (!el.style.getPropertyValue('--rd')) el.style.setProperty('--rd', (i * 95) + 'ms');
            el.classList.add('is-in');
            io.unobserve(el);
          });
          obs.disconnect();
        });
      }, { rootMargin: '0px 0px -10% 0px', threshold: 0.05 });
      rio.observe(railEl);
    });
  })();

  /* ══════════════════════════════════════════════════════════════
     8) العدّادات الرقمية
     ══════════════════════════════════════════════════════════════ */
  (function counters() {
    var nodes = $$('.count');
    if (!nodes.length) return;

    function run(el) {
      var target = parseFloat(el.getAttribute('data-count')) || 0;
      var dec = parseInt(el.getAttribute('data-decimals') || '0', 10);
      var suffix = el.getAttribute('data-suffix') || '';
      if (reduced.matches) { el.textContent = target.toFixed(dec) + suffix; return; }

      var dur = 1500, t0 = null;
      function step(ts) {
        if (t0 === null) t0 = ts;
        var p = clamp((ts - t0) / dur, 0, 1);
        var eased = 1 - Math.pow(1 - p, 4);
        el.textContent = (target * eased).toFixed(dec) + suffix;
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    }

    if (!('IntersectionObserver' in window)) { nodes.forEach(run); return; }
    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        run(e.target);
        obs.unobserve(e.target);
      });
    }, { threshold: 0.5 });
    nodes.forEach(function (n) { io.observe(n); });
  })();

  /* ══════════════════════════════════════════════════════════════
     9) البارالاكس الناعم (حلقة rAF مع تنعيم)
     ══════════════════════════════════════════════════════════════ */
  (function parallax() {
    var items = $$('[data-parallax]');
    if (!items.length || reduced.matches) return;

    var state = items.map(function (el) {
      return { el: el, f: parseFloat(el.getAttribute('data-parallax')) || 0, cur: 0, goal: 0 };
    });
    var running = false, vh = window.innerHeight;

    function measure() {
      vh = window.innerHeight;
      state.forEach(function (s) {
        var r = s.el.getBoundingClientRect();
        var center = r.top + r.height / 2;
        s.goal = clamp((center - vh / 2) / vh, -1.4, 1.4) * s.f * 92;
      });
    }

    function tick() {
      var moving = false;
      state.forEach(function (s) {
        s.cur = lerp(s.cur, s.goal, 0.085);
        if (Math.abs(s.cur - s.goal) > 0.08) moving = true;
        s.el.style.setProperty('--py', s.cur.toFixed(2) + 'px');
        s.el.style.translate = '0 ' + s.cur.toFixed(2) + 'px';
      });
      if (moving) { requestAnimationFrame(tick); } else { running = false; }
    }

    function kick() {
      measure();
      if (!running) { running = true; requestAnimationFrame(tick); }
    }

    window.addEventListener('scroll', kick, { passive: true });
    window.addEventListener('resize', kick);
    kick();
  })();

  /* ══════════════════════════════════════════════════════════════
     10) الميلان ثلاثي الأبعاد + الأزرار المغناطيسية + توهّج البطاقات
     ══════════════════════════════════════════════════════════════ */
  (function pointerFx() {
    /* توهّج يتبع المؤشّر داخل البطاقات */
    $$('.card, .prop, .map-card').forEach(function (card) {
      card.addEventListener('pointermove', function (e) {
        var r = card.getBoundingClientRect();
        card.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100).toFixed(1) + '%');
        card.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100).toFixed(1) + '%');
      }, { passive: true });
    });

    /* استجابة اللمس: تفعيل حالة البطاقة عند النقر على الأجهزة اللمسية */
    var tapped = null;
    $$('[data-tap]').forEach(function (el) {
      el.addEventListener('pointerdown', function (e) {
        if (e.pointerType === 'mouse') return;
        if (tapped && tapped !== el) tapped.classList.remove('is-tapped');
        el.classList.add('is-tapped');
        tapped = el;
        var r = el.getBoundingClientRect();
        el.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100).toFixed(1) + '%');
        el.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100).toFixed(1) + '%');
      }, { passive: true });
    });
    document.addEventListener('pointerdown', function (e) {
      if (tapped && !tapped.contains(e.target)) { tapped.classList.remove('is-tapped'); tapped = null; }
    }, { passive: true, capture: true });

    if (reduced.matches || !finePointer.matches) return;

    /* الميلان */
    $$('[data-tilt]').forEach(function (el) {
      var raf = null, rx = 0, ry = 0;
      function apply() { el.style.transform = 'perspective(1100px) rotateX(' + rx + 'deg) rotateY(' + ry + 'deg)'; raf = null; }
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5;
        var py = (e.clientY - r.top) / r.height - 0.5;
        rx = clamp(-py * 7, -7, 7);
        ry = clamp(px * 7, -7, 7);
        if (!raf) raf = requestAnimationFrame(apply);
      }, { passive: true });
      el.addEventListener('pointerleave', function () { rx = 0; ry = 0; if (!raf) raf = requestAnimationFrame(apply); });
    });

    /* الأزرار المغناطيسية */
    $$('.magnet').forEach(function (el) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left - r.width / 2) * 0.16;
        var y = (e.clientY - r.top - r.height / 2) * 0.22;
        el.style.translate = x.toFixed(1) + 'px ' + y.toFixed(1) + 'px';
      }, { passive: true });
      el.addEventListener('pointerleave', function () { el.style.translate = '0 0'; });
    });
  })();

  /* ══════════════════════════════════════════════════════════════
     11) سكة العروض — سحب باللمس + نقاط + أزرار
     ══════════════════════════════════════════════════════════════ */
  (function rail() {
    var wrap = $('[data-rail]');
    if (!wrap) return;
    var track = $('.rail__track', wrap);
    var dotsBox = $('#railDots');
    var prev = $('[data-rail-prev]', wrap);
    var next = $('[data-rail-next]', wrap);
    if (!track) return;

    var items = $$(':scope > *', track);
    var dots = [];

    items.forEach(function (_, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'rail__dot';
      b.setAttribute('role', 'tab');
      b.setAttribute('aria-label', 'الانتقال إلى العرض رقم ' + (i + 1));
      b.addEventListener('click', function () { goTo(i); });
      if (dotsBox) dotsBox.appendChild(b);
      dots.push(b);
    });

    function isScrollable() { return track.scrollWidth - track.clientWidth > 8; }

    function activeIndex() {
      var tr = track.getBoundingClientRect();
      var mid = tr.left + tr.width / 2;
      var best = 0, bestD = Infinity;
      items.forEach(function (el, i) {
        var r = el.getBoundingClientRect();
        var d = Math.abs((r.left + r.width / 2) - mid);
        if (d < bestD) { bestD = d; best = i; }
      });
      return best;
    }

    function goTo(i) {
      i = clamp(i, 0, items.length - 1);
      var el = items[i];
      var tr = track.getBoundingClientRect();
      var r = el.getBoundingClientRect();
      var delta = (r.left + r.width / 2) - (tr.left + tr.width / 2);
      track.scrollBy({ left: delta, behavior: reduced.matches ? 'auto' : 'smooth' });
    }

    function sync() {
      if (!isScrollable()) {
        if (wrap.querySelector('.rail__nav')) wrap.querySelector('.rail__nav').style.display = 'none';
        return;
      }
      if (wrap.querySelector('.rail__nav')) wrap.querySelector('.rail__nav').style.display = '';
      var i = activeIndex();
      dots.forEach(function (d, k) {
        d.classList.toggle('is-active', k === i);
        d.setAttribute('aria-selected', String(k === i));
      });
      if (prev) prev.disabled = i <= 0;
      if (next) next.disabled = i >= items.length - 1;
    }

    if (prev) prev.addEventListener('click', function () { goTo(activeIndex() - 1); });
    if (next) next.addEventListener('click', function () { goTo(activeIndex() + 1); });

    var t = null;
    track.addEventListener('scroll', function () {
      clearTimeout(t);
      t = setTimeout(sync, 90);
    }, { passive: true });
    window.addEventListener('resize', sync);
    sync();

    /* السحب بالماوس على الأجهزة المكتبية */
    if (finePointer.matches) {
      var down = false, startX = 0, startScroll = 0, moved = false;
      track.addEventListener('pointerdown', function (e) {
        if (e.pointerType !== 'mouse' || !isScrollable()) return;
        down = true; moved = false;
        startX = e.clientX; startScroll = track.scrollLeft;
        track.style.cursor = 'grabbing';
      });
      window.addEventListener('pointermove', function (e) {
        if (!down) return;
        var dx = e.clientX - startX;
        if (Math.abs(dx) > 4) moved = true;
        track.scrollLeft = startScroll - dx;
      });
      window.addEventListener('pointerup', function () {
        if (!down) return;
        down = false;
        track.style.cursor = '';
        if (moved) { setTimeout(function () { goTo(activeIndex()); }, 40); }
      });
      track.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); } }, true);
    }
  })();

  /* ══════════════════════════════════════════════════════════════
     12) خط تقدّم خطوات العمل
     ══════════════════════════════════════════════════════════════ */
  (function stepsLine() {
    var wrap = $('#steps');
    if (!wrap || reduced.matches) return;
    var path = $('.steps__prog', wrap);
    if (!path) return;
    var LEN = 1188, ticking = false;

    function update() {
      var r = wrap.getBoundingClientRect();
      var vh = window.innerHeight;
      var p = clamp((vh * 0.85 - r.top) / (r.height * 0.55), 0, 1);
      path.style.strokeDashoffset = (LEN * (1 - p)).toFixed(1);
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener('resize', update);
    update();
  })();

  /* ══════════════════════════════════════════════════════════════
     13) الأسئلة الشائعة — فتح واحد في كل مرّة
     ══════════════════════════════════════════════════════════════ */
  (function accordion() {
    var items = $$('#acc .acc__item');
    items.forEach(function (d) {
      d.addEventListener('toggle', function () {
        if (!d.open) return;
        items.forEach(function (o) { if (o !== d) o.open = false; });
      });
    });
  })();

  /* ══════════════════════════════════════════════════════════════
     14) نموذج التواصل → رسالة واتساب جاهزة
     ══════════════════════════════════════════════════════════════ */
  (function form() {
    var form = $('#contactForm');
    if (!form) return;
    var note = $('#formNote');

    var RULES = {
      name: {
        test: function (v) { return v.trim().length >= 2; },
        msg: 'يرجى كتابة الاسم (حرفان على الأقل).'
      },
      phone: {
        test: function (v) { return /^(?:\+?966|00966|0)?5\d{8}$/.test(v.replace(/[\s\-()]/g, '')); },
        msg: 'أدخل رقم جوال سعودي صحيح، مثل 0501234567.'
      }
    };

    function setError(field, msg) {
      var wrap = field.closest('.field');
      var err = wrap ? $('[data-err]', wrap) : null;
      if (wrap) wrap.classList.toggle('is-invalid', !!msg);
      if (err) err.textContent = msg || '';
      field.setAttribute('aria-invalid', msg ? 'true' : 'false');
    }

    function validate(field) {
      var rule = RULES[field.name];
      if (!rule) return true;
      var ok = rule.test(field.value);
      setError(field, ok ? '' : rule.msg);
      return ok;
    }

    Object.keys(RULES).forEach(function (n) {
      var f = form.elements[n];
      if (!f) return;
      f.addEventListener('blur', function () { validate(f); });
      f.addEventListener('input', function () {
        if (f.closest('.field').classList.contains('is-invalid')) validate(f);
      });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = true, firstBad = null;
      Object.keys(RULES).forEach(function (n) {
        var f = form.elements[n];
        if (f && !validate(f)) { ok = false; if (!firstBad) firstBad = f; }
      });

      if (!ok) {
        if (note) note.textContent = 'يرجى تصحيح الحقول المُعلَّمة قبل الإرسال.';
        if (firstBad) firstBad.focus();
        return;
      }

      var name = form.elements.name.value.trim();
      var phone = form.elements.phone.value.trim();
      var type = form.elements.type.value;
      var msg = form.elements.message.value.trim();

      var text =
        'السلام عليكم، معكم ' + name + '.\n' +
        'نوع الطلب: ' + type + '\n' +
        'رقم التواصل: ' + phone +
        (msg ? '\nالتفاصيل: ' + msg : '') +
        '\n\n— أُرسلت من الموقع الإلكتروني';

      if (note) note.textContent = 'جارٍ فتح واتساب… راجع الرسالة ثم أرسلها.';
      window.open(LINKS.wa(text), '_blank', 'noopener');
      setTimeout(function () {
        if (note) note.textContent = 'تم تجهيز رسالتك. إن لم تُفتح نافذة واتساب، تأكّد من السماح بالنوافذ المنبثقة.';
      }, 900);
    });
  })();

  /* ══════════════════════════════════════════════════════════════
     15) لمسات أخيرة
     ══════════════════════════════════════════════════════════════ */
  (function misc() {
    var y = $('#year');
    if (y) y.textContent = new Date().getFullYear();

    /* لمعة دورية على شعار الترويسة */
    var brand = $('.header .brand__mark');
    if (brand && !reduced.matches) {
      setInterval(function () {
        if (document.hidden) return;
        brand.classList.add('is-gleaming');
        setTimeout(function () { brand.classList.remove('is-gleaming'); }, 1300);
      }, 9000);
    }

    /* تمرير ناعم مع مراعاة ارتفاع الترويسة */
    $$('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var id = a.getAttribute('href');
        if (!id || id === '#') return;
        var target = document.querySelector(id);
        if (!target) return;
        e.preventDefault();
        var top = target.getBoundingClientRect().top + window.scrollY -
                  (parseInt(getComputedStyle(root).getPropertyValue('--header-h'), 10) || 76) - 14;
        window.scrollTo({ top: top, behavior: reduced.matches ? 'auto' : 'smooth' });
        if (history.replaceState) history.replaceState(null, '', id);
      });
    });
  })();

})();
