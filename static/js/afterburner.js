/* =====================================================================
   AFTERBURNER — site-wide behaviour
   Loaded on every page by base.html. Each module looks for its own
   elements first, so pages without them are unaffected.
   ===================================================================== */
(function () {
    'use strict';

    window.__afterburner = true;

    var doc = document.documentElement;
    var mq = function (q) { return !!(window.matchMedia && window.matchMedia(q).matches); };
    var reduceMotion = mq('(prefers-reduced-motion: reduce)');
    var finePointer = mq('(hover: hover) and (pointer: fine)');
    var hasIO = 'IntersectionObserver' in window;

    function $(sel, root) { return (root || document).querySelector(sel); }
    function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

    function store(key, value) {
        try {
            if (value === undefined) return localStorage.getItem(key);
            localStorage.setItem(key, value);
        } catch (e) { return null; }
    }

    function session(key, value) {
        try {
            if (value === undefined) return sessionStorage.getItem(key);
            sessionStorage.setItem(key, value);
        } catch (e) { return null; }
    }

    function mode() { return doc.getAttribute('data-clearance') === 'unclassified' ? 'unclassified' : 'classified'; }
    function classified() { return mode() === 'classified'; }
    function lively() { return classified() && !reduceMotion; }

    function pad3(n) { return n < 1000 ? ('00' + n).slice(-3) : String(n); }

    function announce(text) {
        var el = document.getElementById('ab-announce');
        if (!el) return;
        el.textContent = '';
        setTimeout(function () { el.textContent = text; }, 30);
    }

    function ready(fn) {
        if (document.readyState !== 'loading') fn();
        else document.addEventListener('DOMContentLoaded', fn);
    }

    /* ----------------------------------------------------------------
       Clearance toggle (Classified / Unclassified), remembered across pages
       ---------------------------------------------------------------- */
    var modeListeners = [];
    function onModeChange(fn) { modeListeners.push(fn); }

    function setMode(next, opts) {
        if (next !== 'classified' && next !== 'unclassified') return;
        var changed = next !== mode();
        doc.setAttribute('data-clearance', next);
        store('ab-clearance', next);
        syncClearanceSwitch();
        if (!changed) return;
        if (!(opts && opts.silent)) announce(next === 'classified' ? 'Classified mode' : 'Unclassified mode');
        if (document.body.classList.contains('ab-home')) window.scrollTo(0, 0);
        modeListeners.forEach(function (fn) { fn(next); });
    }

    function syncClearanceSwitch() {
        var btn = document.getElementById('ab-clearance');
        if (btn) btn.setAttribute('aria-checked', String(classified()));
    }

    function initClearance() {
        var btn = document.getElementById('ab-clearance');
        if (!btn) return;
        syncClearanceSwitch();
        btn.addEventListener('click', function () {
            setMode(classified() ? 'unclassified' : 'classified');
        });
    }

    /* ----------------------------------------------------------------
       Cold start → power-up
       ---------------------------------------------------------------- */
    var powered = false;
    var poweredListeners = [];
    function onPowered(fn) { if (powered) fn(); else poweredListeners.push(fn); }

    function markPowered() {
        if (powered) return;
        powered = true;
        doc.classList.add('ab-powered');
        poweredListeners.forEach(function (fn) { fn(); });
        poweredListeners = [];
    }

    function initColdStart() {
        if (!doc.classList.contains('ab-cold')) { markPowered(); return; }

        var startBtn = document.getElementById('ab-start');
        var started = false;
        var auto = setTimeout(start, 4000); // nobody waits behind a button

        if (startBtn) setTimeout(function () { startBtn.focus({ preventScroll: true }); }, 50);

        function start() {
            if (started) return;
            started = true;
            clearTimeout(auto);
            window.removeEventListener('keydown', start, true);
            if (startBtn) startBtn.removeEventListener('click', start);
            store('ab-cold-start', '1');

            if (reduceMotion) {
                doc.classList.remove('ab-cold');
                markPowered();
                return;
            }

            doc.classList.add('ab-powering');
            setTimeout(function () {
                doc.classList.remove('ab-cold', 'ab-powering');
                markPowered();
            }, 780);
        }

        window.addEventListener('keydown', start, true);
        if (startBtn) startBtn.addEventListener('click', start);
    }

    /* ----------------------------------------------------------------
       Hero entrance (one orchestrated moment, after power-up)
       ---------------------------------------------------------------- */
    function initReveals() {
        var items = $$('.ab-reveal, .ab-mfd');
        if (!items.length) return;

        if (!hasIO) { items.forEach(function (el) { el.classList.add('is-inview'); }); return; }

        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-inview');
                    io.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });

        items.forEach(function (el) { io.observe(el); });
    }

    /* ----------------------------------------------------------------
       Full-screen menu
       ---------------------------------------------------------------- */
    function initMenu() {
        var toggle = document.getElementById('ab-menu-toggle');
        var overlay = document.getElementById('ab-overlay');
        if (!toggle || !overlay) return;

        var label = $('.ab-menu-label', toggle);

        function isOpen() { return overlay.classList.contains('is-open'); }

        function setOpen(open) {
            overlay.classList.toggle('is-open', open);
            toggle.classList.toggle('is-open', open);
            doc.classList.toggle('ab-nav-open', open);
            toggle.setAttribute('aria-expanded', String(open));
            toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
            overlay.setAttribute('aria-hidden', String(!open));
            if (open) overlay.removeAttribute('inert'); else overlay.setAttribute('inert', '');
            if (label) label.textContent = open ? 'Close' : 'Menu';
            if (open) {
                var first = $('a', overlay);
                if (first) setTimeout(function () { first.focus({ preventScroll: true }); }, 60);
            }
        }

        toggle.addEventListener('click', function () { setOpen(!isOpen()); });
        $$('a', overlay).forEach(function (a) { a.addEventListener('click', function () { setOpen(false); }); });

        document.addEventListener('keydown', function (e) {
            if (!isOpen()) return;
            if (e.key === 'Escape') { setOpen(false); toggle.focus(); return; }
            if (e.key === 'Tab') {
                var clearance = document.getElementById('ab-clearance');
                var focusables = [clearance, toggle].filter(Boolean).concat($$('a', overlay));
                var first = focusables[0], last = focusables[focusables.length - 1];
                if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
                else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
            }
        });
    }

    /* ----------------------------------------------------------------
       HUD altitude ladder: scroll progress + section waypoints.
       Top of the page is cruising altitude; the footer is touchdown.
       ---------------------------------------------------------------- */
    function initLadder() {
        var ladder = document.getElementById('ab-ladder');
        var sections = $$('[data-ab-waypoint]');
        if (!ladder || sections.length < 3) return;

        var CRUISE = 30000;
        ladder.innerHTML = '';

        var readout = document.createElement('div');
        readout.className = 'ab-ladder-readout';
        readout.innerHTML = 'Alt <span>30000</span>';
        var readoutValue = readout.querySelector('span');

        var tape = document.createElement('div');
        tape.className = 'ab-ladder-tape';
        var caret = document.createElement('span');
        caret.className = 'ab-ladder-caret';
        tape.appendChild(caret);

        ladder.appendChild(readout);
        ladder.appendChild(tape);

        var points = sections.map(function (section) {
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'ab-ladder-wp';
            btn.textContent = section.getAttribute('data-ab-waypoint');
            btn.addEventListener('click', function () {
                section.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
            });
            ladder.appendChild(btn);
            return { el: section, btn: btn, at: 0 };
        });

        var maxScroll = 1;

        function layout() {
            maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
            points.forEach(function (p) {
                var visible = p.el.offsetParent !== null || p.el.tagName === 'FOOTER';
                p.btn.hidden = !visible;
                var top = p.el.getBoundingClientRect().top + window.scrollY;
                p.at = Math.min(1, Math.max(0, top / maxScroll));
            });
            // keep labels apart when sections sit close together near the end of the page
            var GAP = 0.09, shown = points.filter(function (p) { return !p.btn.hidden; });
            for (var i = shown.length - 2; i >= 0; i--) {
                shown[i].at = Math.min(shown[i].at, shown[i + 1].at - GAP);
            }
            for (var k = 1; k < shown.length; k++) {
                shown[k].at = Math.max(shown[k].at, shown[k - 1].at + GAP);
            }
            points.forEach(function (p) { p.btn.style.top = (Math.min(1, Math.max(0, p.at)) * 100) + '%'; });
            update();
        }

        function update() {
            var y = window.scrollY || 0;
            var progress = Math.min(1, Math.max(0, y / maxScroll));
            ladder.style.setProperty('--p', progress.toFixed(4));
            readoutValue.textContent = ('0000' + Math.round((1 - progress) * CRUISE / 100) * 100).slice(-5);

            var line = window.innerHeight * 0.4;
            var active = null;
            points.forEach(function (p) {
                if (p.btn.hidden) return;
                if (p.el.getBoundingClientRect().top <= line) active = p;
            });
            if (!active) active = points[0];
            if (y >= maxScroll - 2) active = points[points.length - 1];
            points.forEach(function (p) { p.btn.classList.toggle('is-active', p === active); });
        }

        var ticking = false;
        window.addEventListener('scroll', function () {
            if (ticking) return;
            ticking = true;
            requestAnimationFrame(function () { ticking = false; update(); });
        }, { passive: true });
        window.addEventListener('resize', layout);
        window.addEventListener('load', layout);
        onModeChange(function () { setTimeout(layout, 50); });
        if (document.fonts && document.fonts.ready) document.fonts.ready.then(layout);

        ladder.hidden = false;
        ladder.classList.add('is-ready');
        layout();
    }

    /* ----------------------------------------------------------------
       Reticle cursor + lock-on brackets (desktop, Classified)
       ---------------------------------------------------------------- */
    function initReticle() {
        var reticle = document.getElementById('ab-reticle');
        var lock = document.getElementById('ab-lock');
        if (!reticle || !lock || !finePointer || reduceMotion) return;

        var CLICKABLE = 'a[href], button, [role="button"], [role="switch"], summary, label[for], select, ' +
            'input[type="checkbox"], input[type="radio"], input[type="submit"], input[type="button"]';
        var TEXT = 'input:not([type="checkbox"]):not([type="radio"]):not([type="submit"]):not([type="button"]), textarea, select, [contenteditable]';

        var x = -100, y = -100, raf = null, target = null, enabled = false;

        function enable(on) {
            enabled = on;
            doc.classList.toggle('ab-reticle-on', on);
            if (!on) release();
        }

        function paint() {
            raf = null;
            reticle.style.transform = 'translate3d(' + x + 'px,' + y + 'px,0)';
            if (target) place(false);
        }

        function place(fresh) {
            var r = target.getBoundingClientRect();
            if (!r.width && !r.height) { release(); return; }
            var padTight = 6, padWide = 16;
            if (fresh) {
                lock.classList.add('is-instant');
                setRect(r, padWide);
                void lock.offsetWidth;
                lock.classList.remove('is-instant');
            }
            setRect(r, padTight);
            lock.classList.add('is-locked');
        }

        function setRect(r, pad) {
            lock.style.width = (r.width + pad * 2) + 'px';
            lock.style.height = (r.height + pad * 2) + 'px';
            lock.style.transform = 'translate3d(' + (r.left - pad) + 'px,' + (r.top - pad) + 'px,0)';
        }

        function release() {
            target = null;
            lock.classList.remove('is-locked');
        }

        document.addEventListener('pointermove', function (e) {
            if (!enabled || e.pointerType !== 'mouse') return;
            x = e.clientX; y = e.clientY;

            var el = e.target instanceof Element ? e.target : null;
            var overText = el && el.closest(TEXT);
            reticle.classList.toggle('is-hidden', !!overText);

            var next = el && !overText ? el.closest(CLICKABLE) : null;
            if (next && (next.hasAttribute('data-ab-target') || next.closest('[data-ab-target]'))) next = null; // radar blips have their own lock
            if (next !== target) {
                if (next) { target = next; place(true); } else { release(); }
            }
            if (!raf) raf = requestAnimationFrame(paint);
        }, { passive: true });

        doc.addEventListener('mouseleave', function () { reticle.classList.add('is-hidden'); release(); });
        doc.addEventListener('mouseenter', function () { reticle.classList.remove('is-hidden'); });
        window.addEventListener('scroll', function () { if (target && !raf) raf = requestAnimationFrame(paint); }, { passive: true });

        enable(classified());
        onModeChange(function (m) { enable(m === 'classified'); });
    }

    /* ----------------------------------------------------------------
       Ambient node canvas (whole page, cursor-reactive, Classified only)
       ---------------------------------------------------------------- */
    function initCanvas() {
        var canvas = document.getElementById('ab-canvas');
        if (!canvas || !canvas.getContext) return;

        var ctx = canvas.getContext('2d');
        var dpr = Math.min(window.devicePixelRatio || 1, 2);
        var LINK = 150, REACH = 190;
        var w = 0, h = 0, lastW = 0;
        var nodes = [];
        var mouse = { x: 0, y: 0, active: false };
        var lastScroll = window.scrollY || 0;
        var rafId = null;

        function seed() {
            var count = Math.round(Math.min(95, Math.max(28, (w * h) / 15000)));
            nodes = [];
            for (var i = 0; i < count; i++) {
                nodes.push({
                    x: Math.random() * w,
                    y: Math.random() * h,
                    vx: (Math.random() - 0.5) * 0.16,
                    vy: (Math.random() - 0.5) * 0.16,
                    red: Math.random() < 0.035
                });
            }
        }

        function resize() {
            w = window.innerWidth;
            h = window.innerHeight;
            canvas.width = Math.round(w * dpr);
            canvas.height = Math.round(h * dpr);
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            if (w !== lastW || !nodes.length) seed(); // mobile toolbar resizes only change height
            lastW = w;
            if (!rafId && classified()) draw();
        }

        function wrap(n) {
            if (n.x < -20) n.x = w + 20; else if (n.x > w + 20) n.x = -20;
            if (n.y < -20) n.y = h + 20; else if (n.y > h + 20) n.y = -20;
        }

        function step() {
            for (var i = 0; i < nodes.length; i++) {
                var n = nodes[i];
                n.x += n.vx; n.y += n.vy;
                if (mouse.active) {
                    var dx = n.x - mouse.x, dy = n.y - mouse.y, d2 = dx * dx + dy * dy;
                    if (d2 < 8100 && d2 > 0.01) {
                        var d = Math.sqrt(d2), push = (1 - d / 90) * 0.6;
                        n.x += (dx / d) * push; n.y += (dy / d) * push;
                    }
                }
                wrap(n);
            }
        }

        function draw() {
            ctx.clearRect(0, 0, w, h);
            var i, j, a, b, dx, dy, d, alpha;

            ctx.setLineDash([2, 4]);
            ctx.lineWidth = 1;
            for (i = 0; i < nodes.length; i++) {
                a = nodes[i];
                for (j = i + 1; j < nodes.length; j++) {
                    b = nodes[j];
                    dx = a.x - b.x; dy = a.y - b.y;
                    if (Math.abs(dx) > LINK || Math.abs(dy) > LINK) continue;
                    d = Math.sqrt(dx * dx + dy * dy);
                    if (d > LINK) continue;
                    alpha = (1 - d / LINK) * 0.2;
                    if (mouse.active) {
                        var mx = (a.x + b.x) / 2 - mouse.x, my = (a.y + b.y) / 2 - mouse.y;
                        var md = Math.sqrt(mx * mx + my * my);
                        if (md < REACH) alpha += (1 - md / REACH) * 0.25;
                    }
                    ctx.strokeStyle = 'rgba(138,147,163,' + alpha.toFixed(3) + ')';
                    ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
                }
            }

            ctx.setLineDash([]);
            if (mouse.active) {
                for (i = 0; i < nodes.length; i++) {
                    a = nodes[i];
                    dx = a.x - mouse.x; dy = a.y - mouse.y;
                    d = Math.sqrt(dx * dx + dy * dy);
                    if (d > REACH) continue;
                    alpha = (1 - d / REACH) * 0.32;
                    ctx.strokeStyle = a.red ? 'rgba(252,0,0,' + (alpha * 1.4).toFixed(3) + ')' : 'rgba(197,202,211,' + alpha.toFixed(3) + ')';
                    ctx.beginPath(); ctx.moveTo(mouse.x, mouse.y); ctx.lineTo(a.x, a.y); ctx.stroke();
                }
            }

            for (i = 0; i < nodes.length; i++) {
                a = nodes[i];
                ctx.fillStyle = a.red ? 'rgba(252,0,0,0.85)' : 'rgba(138,147,163,0.55)';
                ctx.beginPath();
                ctx.arc(a.x, a.y, a.red ? 1.9 : 1.4, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        function loop() { step(); draw(); rafId = requestAnimationFrame(loop); }
        function start() {
            if (!classified()) return;
            if (reduceMotion) { draw(); return; }
            if (!rafId) rafId = requestAnimationFrame(loop);
        }
        function stop() {
            if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
            ctx.clearRect(0, 0, w, h);
        }

        resize();
        window.addEventListener('resize', resize);

        if (finePointer && !reduceMotion) {
            window.addEventListener('pointermove', function (e) {
                if (e.pointerType !== 'mouse') return;
                mouse.x = e.clientX; mouse.y = e.clientY; mouse.active = true;
            }, { passive: true });
            doc.addEventListener('mouseleave', function () { mouse.active = false; });
            window.addEventListener('blur', function () { mouse.active = false; });
        }

        if (!reduceMotion) {
            window.addEventListener('scroll', function () {
                var y = window.scrollY || 0, delta = (y - lastScroll) * 0.18;
                lastScroll = y;
                for (var i = 0; i < nodes.length; i++) { nodes[i].y -= delta; wrap(nodes[i]); }
            }, { passive: true });
        }

        document.addEventListener('visibilitychange', function () {
            if (document.hidden) { if (rafId) { cancelAnimationFrame(rafId); rafId = null; } }
            else start();
        });

        onModeChange(function (m) { if (m === 'classified') start(); else stop(); });
        start();
    }

    /* ----------------------------------------------------------------
       Jakarta clock (OPERATOR caption)
       ---------------------------------------------------------------- */
    function initClock() {
        var els = $$('[data-ab-clock]');
        if (!els.length) return;
        var fmt;
        try {
            fmt = new Intl.DateTimeFormat('en-GB', {
                timeZone: 'Asia/Jakarta', hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23'
            });
        } catch (e) { return; }
        function tick() { var t = fmt.format(new Date()); els.forEach(function (el) { el.textContent = t; }); }
        tick();
        setInterval(tick, 1000);
    }

    /* ----------------------------------------------------------------
       Radar lock-on navigation: blips are the site's pages
       ---------------------------------------------------------------- */
    function initRadarNav() {
        var radar = $('.ab-radar');
        if (!radar) return;
        var nameEl = $('[data-ab-lock-name]', radar);
        var busy = false;

        $$('.ab-blip', radar).forEach(function (blip) {
            blip.addEventListener('click', function (e) {
                if (busy || !lively() || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
                e.preventDefault();
                busy = true;
                var name = blip.getAttribute('data-ab-target') || '';
                if (nameEl) nameEl.textContent = ' · ' + name;
                blip.classList.add('is-target');
                radar.classList.add('is-locked');
                announce('Target locked: ' + name);
                setTimeout(function () { window.location.href = blip.href; }, 520);
            });
        });

        // returning with the back button: clear the lock
        window.addEventListener('pageshow', function () {
            busy = false;
            radar.classList.remove('is-locked');
            $$('.ab-blip.is-target', radar).forEach(function (b) { b.classList.remove('is-target'); });
        });
    }

    /* ----------------------------------------------------------------
       Readouts: count up from zero on power-up; relative "last push"
       ---------------------------------------------------------------- */
    function ago(iso) {
        var t = Date.parse(iso);
        if (isNaN(t)) return null;
        var s = Math.max(0, (Date.now() - t) / 1000);
        if (s < 60) return 'Just now';
        var m = s / 60; if (m < 60) return Math.floor(m) + 'm ago';
        var hr = m / 60; if (hr < 24) return Math.floor(hr) + 'h ago';
        var d = hr / 24; if (d < 30) return Math.floor(d) + 'd ago';
        var mo = d / 30; if (mo < 12) return Math.floor(mo) + 'mo ago';
        return Math.floor(d / 365) + 'y ago';
    }

    function initAgo() {
        $$('[data-ab-ago]').forEach(function (el) {
            var text = ago(el.getAttribute('data-ab-ago'));
            if (text) el.textContent = text.toUpperCase();
        });
    }

    var counted = false;
    function countUp() {
        if (counted) return;
        var els = $$('[data-ab-count]');
        if (!els.length) return;
        if (!lively() || $('.ab-classified') && $('.ab-classified').offsetParent === null) return;
        counted = true;
        var t0 = null, DURATION = 900;
        var targets = els.map(function (el) { return { el: el, to: parseInt(el.getAttribute('data-ab-count'), 10) || 0 }; });
        targets.forEach(function (t) { t.el.textContent = pad3(0); });
        function frame(ts) {
            if (t0 === null) t0 = ts;
            var k = Math.min(1, (ts - t0) / DURATION);
            var eased = 1 - Math.pow(1 - k, 3);
            targets.forEach(function (t) { t.el.textContent = pad3(Math.round(t.to * eased)); });
            if (k < 1) requestAnimationFrame(frame);
        }
        setTimeout(function () { requestAnimationFrame(frame); }, 650);
    }

    /* ----------------------------------------------------------------
       GitHub fallback (only when the server has no telemetry token):
       public REST API from the browser, cached for the session
       ---------------------------------------------------------------- */
    function initGithubFallback() {
        var panel = $('[data-ab-github-fallback]');
        if (!panel || !window.fetch) return;

        var user = panel.getAttribute('data-ab-github-fallback');
        var key = 'ab-github:' + user;
        var TTL = 10 * 60 * 1000;
        var state = $('[data-ab-link-state]', panel);

        function field(name) { return $('[data-ab-field="' + name + '"]', panel); }

        function setState(cls, text) {
            if (!state) return;
            state.classList.remove('is-syncing', 'is-ok', 'is-down');
            state.classList.add(cls);
            state.textContent = text;
        }

        function render(data) {
            var f;
            if ((f = field('repos')) && typeof data.repos === 'number') f.textContent = pad3(data.repos);
            if ((f = field('followers')) && typeof data.followers === 'number') f.textContent = pad3(data.followers);
            if ((f = field('pushed')) && data.pushedAt) f.textContent = (ago(data.pushedAt) || '—').toUpperCase();
            if ((f = field('repo')) && data.repo) {
                f.textContent = ' · Active ';
                var a = document.createElement('a');
                a.href = 'https://github.com/' + encodeURIComponent(user) + '/' + encodeURIComponent(data.repo);
                a.target = '_blank';
                a.rel = 'noopener noreferrer';
                a.textContent = data.repo;
                f.appendChild(a);
            }
            setState('is-ok', 'Link ok');
        }

        function getJSON(url) {
            var ctrl = 'AbortController' in window ? new AbortController() : null;
            var timer = ctrl ? setTimeout(function () { ctrl.abort(); }, 8000) : null;
            return fetch(url, ctrl ? { signal: ctrl.signal } : undefined).then(function (res) {
                if (timer) clearTimeout(timer);
                if (!res.ok) throw new Error('HTTP ' + res.status);
                return res.json();
            });
        }

        var cached = null;
        try { cached = JSON.parse(session(key) || 'null'); } catch (e) { cached = null; }
        if (cached && Date.now() - cached.at < TTL) { render(cached); return; }

        setState('is-syncing', 'Syncing');
        var base = 'https://api.github.com/users/' + encodeURIComponent(user);
        Promise.all([getJSON(base), getJSON(base + '/repos?sort=pushed&per_page=1')])
            .then(function (res) {
                var profile = res[0] || {}, latest = Array.isArray(res[1]) && res[1][0] ? res[1][0] : null;
                var data = {
                    repos: profile.public_repos,
                    followers: profile.followers,
                    pushedAt: latest ? latest.pushed_at : null,
                    repo: latest ? latest.name : null,
                    at: Date.now()
                };
                session(key, JSON.stringify(data));
                render(data);
            })
            .catch(function () {
                if (cached) render(cached); else setState('is-down', 'No link');
            });
    }

    /* ----------------------------------------------------------------
       Stack marquee: repeat the list until it can loop seamlessly
       ---------------------------------------------------------------- */
    function initMarquee() {
        var track = $('.ab-marquee-track');
        if (!track || reduceMotion) return;
        var done = false;

        function build() {
            if (done || track.offsetParent === null) return;
            var list = $('.ab-marquee-list', track);
            var viewport = track.parentElement;
            var items = $$('li', list).map(function (li) { return li.textContent; });
            if (!items.length) return;
            done = true;
            var guard = 0;
            while (list.scrollWidth < viewport.clientWidth && guard++ < 30) {
                items.forEach(function (text) {
                    var li = document.createElement('li');
                    li.textContent = text;
                    li.setAttribute('aria-hidden', 'true');
                    list.appendChild(li);
                });
            }
            var clone = list.cloneNode(true);
            clone.setAttribute('aria-hidden', 'true');
            track.appendChild(clone);
            track.style.setProperty('--ab-marquee-time', Math.max(20, list.scrollWidth / 45).toFixed(1) + 's');
            track.classList.add('is-running');
            viewport.classList.add('is-running');
        }

        build();
        onModeChange(function (m) { if (m === 'classified') setTimeout(build, 30); });
    }

    /* ----------------------------------------------------------------
       Comms banner: lines typed out like a radio transmission
       ---------------------------------------------------------------- */
    function initComms() {
        var body = $('[data-ab-type]');
        if (!body || reduceMotion || !hasIO) return;

        var lines = $$('p', body).map(function (p) {
            var text = p.textContent.trim();
            p.textContent = '';
            var sr = document.createElement('span');
            sr.className = 'ab-sr';
            sr.textContent = text;
            // the untyped rest stays in place (invisible) so the banner never reflows while typing
            var typed = document.createElement('span');
            typed.className = 'ab-typed';
            typed.setAttribute('aria-hidden', 'true');
            var vis = document.createElement('span');
            vis.className = 'ab-typed-vis';
            var ghost = document.createElement('span');
            ghost.className = 'ab-typed-ghost';
            ghost.textContent = text;
            typed.appendChild(vis);
            typed.appendChild(ghost);
            p.appendChild(sr);
            p.appendChild(typed);
            return { p: p, vis: vis, ghost: ghost, text: text };
        });

        function type() {
            var li = 0;
            function nextLine() {
                if (li >= lines.length) return;
                var line = lines[li++], ci = 0;
                line.p.classList.add('is-typing');
                (function nextChar() {
                    if (ci <= line.text.length) {
                        line.vis.textContent = line.text.slice(0, ci);
                        line.ghost.textContent = line.text.slice(ci++);
                        setTimeout(nextChar, 24);
                    } else {
                        if (li < lines.length) line.p.classList.remove('is-typing');
                        setTimeout(nextLine, 260);
                    }
                })();
            }
            nextLine();
        }

        var io = new IntersectionObserver(function (entries) {
            if (entries[0].isIntersecting && classified()) {
                io.disconnect();
                type();
            }
        }, { threshold: 0.35 });
        io.observe(body);
    }

    /* ----------------------------------------------------------------
       Print button (Unclassified CV)
       ---------------------------------------------------------------- */
    function initPrint() {
        $$('[data-ab-print]').forEach(function (btn) {
            btn.addEventListener('click', function () { window.print(); });
        });
    }

    /* ---------------------------------------------------------------- */
    ready(function () {
        initClearance();
        initMenu();
        initClock();
        initAgo();
        initRadarNav();
        initGithubFallback();
        initPrint();
        initCanvas();
        initReticle();
        initLadder();
        initMarquee();
        initComms();

        onModeChange(function (m) { if (m === 'classified') countUp(); });

        initColdStart();
        onPowered(function () {
            requestAnimationFrame(function () {
                initReveals();
                countUp();
            });
        });
    });
})();
