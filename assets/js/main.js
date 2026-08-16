/* ============================================================
   إعمار الشعلة — Interaction Layer
   Zero dependencies. Motion is rAF-driven and respects
   prefers-reduced-motion throughout.
   ============================================================ */
(() => {
  'use strict';

  /* ---------- Site config: change contact details here ---------- */
  const SITE = {
    phone:     '+966560420282',   // اتصال
    whatsapp:  '966561915272',    // واتساب (بدون +)
    mapsQuery: 'مكتب+إعمار+الشعلة+للخدمات+العقارية،+الدمام'
  };

  const $  = (s, ctx = document) => ctx.querySelector(s);
  const $$ = (s, ctx = document) => [...ctx.querySelectorAll(s)];

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = window.matchMedia('(hover:hover) and (pointer:fine)');
  const lessMotion = () => reduced.matches;

  const clamp = (v, a, b) => Math.min(Math.max(v, a), b);
  const lerp  = (a, b, t) => a + (b - a) * t;

  /* ============================================================
     1. PRELOADER
     ============================================================ */
  const preloader = $('#preloader');
  const dismissPreloader = () => {
    if (!preloader || preloader.classList.contains('is-done')) return;
    preloader.classList.add('is-done');
    document.body.classList.add('is-ready');
    startHeroText();
  };

  if (lessMotion()) {
    preloader?.remove();
    document.body.classList.add('is-ready');
  } else {
    window.addEventListener('load', () => setTimeout(dismissPreloader, 700));
    // Safety net: never trap the user behind a stuck preloader
    setTimeout(dismissPreloader, 3600);
  }

  /* ============================================================
     2. SPLIT TEXT — per-word hero reveal
     ============================================================ */
  const splits = $$('[data-split]');

  /* Arabic is a cursive script: its letters change shape according to
     their neighbours and join into one continuous stroke. Wrapping each
     CHARACTER in its own element severs those joins and renders the
     headline as isolated, unreadable glyphs. So we split on whitespace
     only -- word gaps are exactly where Arabic letters already break. */
  splits.forEach(el => {
    const text = el.textContent.trim();

    const frag = document.createDocumentFragment();
    const words = text.split(/\s+/);

    words.forEach((word, i) => {
      const span = document.createElement('span');
      span.className = 'w';
      span.textContent = word;
      span.style.animationDelay = `${i * 0.085}s`;
      frag.appendChild(span);
      // Restore the inter-word space that inline-block would swallow
      if (i < words.length - 1) frag.appendChild(document.createTextNode(' '));
    });

    el.textContent = '';
    el.appendChild(frag);
  });

  let heroStarted = false;
  function startHeroText() {
    if (heroStarted) return;
    heroStarted = true;
    splits.forEach((el, i) => {
      setTimeout(() => el.classList.add('is-in'), i * 180);
    });
  }
  if (lessMotion()) startHeroText();

  /* ============================================================
     3. REVEAL ON SCROLL
     ============================================================ */
  const revealables = $$('.reveal');

  if (lessMotion() || !('IntersectionObserver' in window)) {
    revealables.forEach(el => el.classList.add('is-in'));
  } else {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });

    revealables.forEach(el => io.observe(el));
  }

  /* ============================================================
     4. ANIMATED COUNTERS
     ============================================================ */
  const counters = $$('[data-count]');

  const runCounter = (el) => {
    const target   = parseFloat(el.dataset.count);
    const decimals = parseInt(el.dataset.decimals || '0', 10);
    const suffix   = el.dataset.suffix || '';
    const isYear   = target > 1900 && decimals === 0;

    if (lessMotion()) {
      el.textContent = (isYear ? target : target.toFixed(decimals)) + suffix;
      return;
    }

    const duration = 1700;
    const from = isYear ? target - 26 : 0;
    const t0 = performance.now();

    const tick = (now) => {
      const p = clamp((now - t0) / duration, 0, 1);
      const eased = 1 - Math.pow(1 - p, 3);          // easeOutCubic
      const val = from + (target - from) * eased;
      el.textContent = (isYear ? Math.round(val) : val.toFixed(decimals)) + suffix;
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };

  if ('IntersectionObserver' in window) {
    const cio = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        runCounter(e.target);
        cio.unobserve(e.target);
      });
    }, { threshold: 0.5 });
    counters.forEach(el => cio.observe(el));
  } else {
    counters.forEach(runCounter);
  }

  /* ============================================================
     5. SCROLL: progress bar, nav state, dock, scrollspy
     ============================================================ */
  const nav       = $('#nav');
  const progress  = $('#scrollProgress');
  const dock      = $('#dock');
  const navLinks  = $$('.nav__link');
  const navPill   = $('#navPill');
  const sections  = navLinks
    .map(a => $(a.getAttribute('href')))
    .filter(Boolean);

  let ticking = false;
  let activeLink = null;

  const movePill = (link) => {
    if (!navPill || !link) return;
    navPill.style.width = `${link.offsetWidth}px`;
    navPill.style.transform = `translateX(${link.offsetLeft - navPill.parentElement.offsetLeft}px)`;
    navPill.classList.add('is-on');
  };

  const onScroll = () => {
    const y = window.scrollY;
    const max = document.documentElement.scrollHeight - window.innerHeight;

    if (progress) progress.style.transform = `scaleX(${max > 0 ? clamp(y / max, 0, 1) : 0})`;
    nav?.classList.toggle('is-stuck', y > 24);
    dock?.classList.toggle('is-on', y > 420);

    // Scrollspy
    const probe = y + window.innerHeight * 0.32;
    let current = null;
    sections.forEach(sec => {
      if (sec.offsetTop <= probe) current = sec;
    });

    if (current) {
      const link = navLinks.find(a => a.getAttribute('href') === `#${current.id}`);
      if (link && link !== activeLink) {
        navLinks.forEach(a => a.classList.remove('is-active'));
        link.classList.add('is-active');
        activeLink = link;
        movePill(link);
      }
    } else if (activeLink) {
      navLinks.forEach(a => a.classList.remove('is-active'));
      activeLink = null;
      navPill?.classList.remove('is-on');
    }

    ticking = false;
  };

  window.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(onScroll);
  }, { passive: true });

  window.addEventListener('resize', () => {
    if (activeLink) movePill(activeLink);
  }, { passive: true });

  onScroll();

  /* ============================================================
     6. MOBILE MENU
     ============================================================ */
  const burger = $('#navBurger');
  const menu   = $('#mobileMenu');
  let menuOpen = false;

  const setMenu = (open) => {
    menuOpen = open;
    burger?.setAttribute('aria-expanded', String(open));
    burger?.setAttribute('aria-label', open ? 'إغلاق القائمة' : 'فتح القائمة');
    document.body.style.overflow = open ? 'hidden' : '';

    if (!menu) return;
    if (open) {
      menu.hidden = false;
      requestAnimationFrame(() => menu.classList.add('is-open'));
    } else {
      menu.classList.remove('is-open');
      setTimeout(() => { if (!menuOpen) menu.hidden = true; }, 460);
    }
  };

  burger?.addEventListener('click', () => setMenu(!menuOpen));
  menu?.addEventListener('click', (e) => { if (e.target === menu) setMenu(false); });
  $$('.mobile-menu__links a, .mobile-menu__actions a').forEach(a =>
    a.addEventListener('click', () => setMenu(false))
  );
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && menuOpen) { setMenu(false); burger?.focus(); }
  });

  /* ============================================================
     7. ACCORDION
     ============================================================ */
  $$('.acc__item').forEach(item => {
    const btn = $('.acc__btn', item);
    btn?.addEventListener('click', () => {
      const willOpen = !item.classList.contains('is-open');
      // Close siblings for a calmer, single-focus reading flow
      item.parentElement?.querySelectorAll('.acc__item.is-open').forEach(other => {
        if (other === item) return;
        other.classList.remove('is-open');
        $('.acc__btn', other)?.setAttribute('aria-expanded', 'false');
      });
      item.classList.toggle('is-open', willOpen);
      btn.setAttribute('aria-expanded', String(willOpen));
    });
  });

  /* ============================================================
     8. TILT — works with mouse AND touch
     ============================================================ */
  const tilts = $$('[data-tilt]');

  if (!lessMotion()) {
    tilts.forEach(el => {
      let raf = null;
      let cur = { x: 0, y: 0 };
      let goal = { x: 0, y: 0 };

      const render = () => {
        cur.x = lerp(cur.x, goal.x, 0.12);
        cur.y = lerp(cur.y, goal.y, 0.12);
        el.style.transform =
          `perspective(900px) rotateX(${cur.y.toFixed(2)}deg) rotateY(${cur.x.toFixed(2)}deg) translateZ(0)`;

        if (Math.abs(cur.x - goal.x) > 0.01 || Math.abs(cur.y - goal.y) > 0.01) {
          raf = requestAnimationFrame(render);
        } else {
          raf = null;
          if (goal.x === 0 && goal.y === 0) el.style.transform = '';
        }
      };

      const start = () => { if (!raf) raf = requestAnimationFrame(render); };

      const track = (clientX, clientY) => {
        const r = el.getBoundingClientRect();
        const px = (clientX - r.left) / r.width;
        const py = (clientY - r.top) / r.height;
        goal.x = (px - 0.5) * 9;
        goal.y = (0.5 - py) * 9;
        // Feed the radial glow on service cards
        el.style.setProperty('--mx', `${px * 100}%`);
        el.style.setProperty('--my', `${py * 100}%`);
        start();
      };

      const reset = () => { goal.x = 0; goal.y = 0; start(); };

      el.addEventListener('pointermove', (e) => {
        if (e.pointerType === 'touch') return;   // touch handled below
        track(e.clientX, e.clientY);
      }, { passive: true });
      el.addEventListener('pointerleave', reset, { passive: true });

      // Touch: a gentle press-tilt, released on lift
      el.addEventListener('touchstart', (e) => {
        const t = e.touches[0];
        if (t) track(t.clientX, t.clientY);
      }, { passive: true });
      el.addEventListener('touchmove', (e) => {
        const t = e.touches[0];
        if (t) track(t.clientX, t.clientY);
      }, { passive: true });
      el.addEventListener('touchend', reset, { passive: true });
      el.addEventListener('touchcancel', reset, { passive: true });
    });
  }

  /* ============================================================
     9. MAGNETIC BUTTONS (fine pointer only)
     ============================================================ */
  if (finePointer.matches && !lessMotion()) {
    $$('[data-magnetic]').forEach(el => {
      el.addEventListener('pointermove', (e) => {
        const r = el.getBoundingClientRect();
        const dx = (e.clientX - (r.left + r.width / 2)) * 0.22;
        const dy = (e.clientY - (r.top + r.height / 2)) * 0.3;
        el.style.transform = `translate(${dx}px, ${dy - 3}px)`;
      }, { passive: true });

      el.addEventListener('pointerleave', () => { el.style.transform = ''; }, { passive: true });
    });
  }

  /* ============================================================
     10. RIPPLE — tactile feedback on every button
     ============================================================ */
  $$('.btn, .dock__btn, .ccard').forEach(el => {
    el.addEventListener('pointerdown', (e) => {
      if (lessMotion()) return;
      const r = el.getBoundingClientRect();
      const size = Math.max(r.width, r.height);
      const ink = document.createElement('span');
      ink.className = 'ripple';
      ink.style.width = ink.style.height = `${size}px`;
      ink.style.left = `${e.clientX - r.left - size / 2}px`;
      ink.style.top  = `${e.clientY - r.top  - size / 2}px`;
      el.appendChild(ink);
      setTimeout(() => ink.remove(), 640);
    }, { passive: true });
  });

  // Light haptic on the primary contact actions (Android/Chrome)
  $$('.dock__btn, .ccard').forEach(el => {
    el.addEventListener('click', () => {
      if (navigator.vibrate) navigator.vibrate(8);
    }, { passive: true });
  });

  /* ============================================================
     11. CURSOR GLOW (desktop ambience)
     ============================================================ */
  const glow = $('#cursorGlow');
  if (glow && finePointer.matches && !lessMotion()) {
    let gx = window.innerWidth / 2, gy = window.innerHeight / 2;
    let tx = gx, ty = gy, grafId = null;

    const glowLoop = () => {
      gx = lerp(gx, tx, 0.09);
      gy = lerp(gy, ty, 0.09);
      glow.style.transform = `translate(${gx}px, ${gy}px) translate(-50%,-50%)`;
      grafId = requestAnimationFrame(glowLoop);
    };

    window.addEventListener('pointermove', (e) => {
      if (e.pointerType !== 'mouse') return;
      tx = e.clientX; ty = e.clientY;
      glow.classList.add('is-on');
      if (!grafId) glowLoop();
    }, { passive: true });

    document.addEventListener('pointerleave', () => glow.classList.remove('is-on'));
  }

  /* ============================================================
     12. PARALLAX (rAF, transform-only)
     ============================================================ */
  const layers = $$('[data-parallax]');
  const inners = $$('[data-parallax-inner]');

  if ((layers.length || inners.length) && !lessMotion()) {
    let praf = false;

    const parallax = () => {
      const y = window.scrollY;
      const vh = window.innerHeight;

      layers.forEach(el => {
        const speed = parseFloat(el.dataset.parallax) || 0;
        el.style.transform = `translate3d(0, ${(y * speed).toFixed(1)}px, 0)`;
      });

      inners.forEach(el => {
        const speed = parseFloat(el.dataset.parallaxInner) || 0;
        const r = el.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) return;
        const mid = (r.top + r.height / 2 - vh / 2) / vh;   // -1 .. 1
        const img = el.querySelector('img');
        if (img) img.style.transform = `translate3d(0, ${(mid * speed * 100).toFixed(1)}px, 0) scale(1.1)`;
      });

      praf = false;
    };

    window.addEventListener('scroll', () => {
      if (praf) return;
      praf = true;
      requestAnimationFrame(parallax);
    }, { passive: true });

    parallax();
  }

  /* ============================================================
     13. LAZY MAP — loads only on tap (privacy + performance)
     ============================================================ */
  const mapBtn = $('#mapLoad');
  mapBtn?.addEventListener('click', () => {
    const frame = document.createElement('iframe');
    frame.src = `https://maps.google.com/maps?q=${SITE.mapsQuery}&z=16&hl=ar&output=embed`;
    frame.loading = 'lazy';
    frame.title = 'موقع مكتب إعمار الشعلة على الخريطة';
    frame.referrerPolicy = 'no-referrer-when-downgrade';
    frame.allowFullscreen = true;
    mapBtn.replaceWith(frame);
  });

  /* ============================================================
     14. SMOOTH ANCHORS (respects reduced motion)
     ============================================================ */
  $$('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (!id || id === '#') return;
      const target = $(id);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({
        behavior: lessMotion() ? 'auto' : 'smooth',
        block: 'start'
      });
      history.replaceState(null, '', id);
    });
  });

  /* ============================================================
     15. MISC
     ============================================================ */
  const yearEl = $('#year');
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  // Keep motion honest if the user flips the OS setting mid-session
  reduced.addEventListener?.('change', () => {
    if (reduced.matches) {
      revealables.forEach(el => el.classList.add('is-in'));
      splits.forEach(el => el.classList.add('is-in'));
    }
  });
})();
