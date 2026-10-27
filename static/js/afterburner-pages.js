/* =====================================================================
   AFTERBURNER — inner pages + easter eggs
   Loaded on every page after afterburner.js. Each module looks for its
   own elements first, so pages without them are unaffected.

   Sorties (flight path) · Ribbon rack · Commend · Messages as toasts ·
   Command line (Ctrl+K) · Night vision (N) · "Some say…"
   ===================================================================== */
(function () {
    'use strict';

    var AB = window.Afterburner || {
        mode: function () { return 'classified'; },
        classified: function () { return true; },
        lively: function () { return false; },
        setMode: function () {},
        onModeChange: function () {},
        onPowered: function (fn) { fn(); },
        announce: function () {},
        store: function () { return null; },
        session: function () { return null; },
        reduceMotion: true,
        finePointer: false
    };

    var doc = document.documentElement;

    function $(sel, root) { return (root || document).querySelector(sel); }
    function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
    function pad2(n) { return n < 10 ? '0' + n : String(n); }

    function ready(fn) {
        if (document.readyState !== 'loading') fn();
        else document.addEventListener('DOMContentLoaded', fn);
    }

    function isTyping(target) {
        if (!(target instanceof Element)) return false;
        return !!target.closest('input, textarea, select, [contenteditable=""], [contenteditable="true"]');
    }

    function toast(title, message, type) {
        if (typeof window.showToast === 'function') window.showToast(title, message, type || 'normal', 3600);
    }

    /* ----------------------------------------------------------------
       Tabs: shared by the waypoints and the ribbons.
       tabs[i] controls panels[i]; onSelect(i, fromUser) runs after.
       ---------------------------------------------------------------- */
    function makeTabs(tabs, panels, onSelect, opts) {
        opts = opts || {};
        var current = Math.max(0, tabs.findIndex(function (t) { return t.getAttribute('aria-selected') === 'true'; }));

        function select(i, fromUser, focus) {
            if (i < 0 || i >= tabs.length) return;
            current = i;
            tabs.forEach(function (tab, k) {
                var on = k === i;
                tab.setAttribute('aria-selected', String(on));
                tab.tabIndex = on ? 0 : -1;
                tab.classList.toggle('is-selected', on);
            });
            panels.forEach(function (panel, k) { panel.hidden = k !== i; });
            if (focus) tabs[i].focus({ preventScroll: true });
            if (onSelect) onSelect(i, fromUser);
        }

        tabs.forEach(function (tab, i) {
            tab.addEventListener('click', function (e) {
                if (opts.shouldIgnoreClick && opts.shouldIgnoreClick(e)) { e.preventDefault(); return; }
                select(i, true, false);
            });
            tab.addEventListener('keydown', function (e) {
                var next = null;
                if (e.key === 'ArrowRight' || e.key === 'ArrowDown') next = (current + 1) % tabs.length;
                else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') next = (current - 1 + tabs.length) % tabs.length;
                else if (e.key === 'Home') next = 0;
                else if (e.key === 'End') next = tabs.length - 1;
                if (next === null) return;
                e.preventDefault();
                select(next, true, true);
            });
        });

        select(current, false, false);
        return { select: select, current: function () { return current; } };
    }

    /* ----------------------------------------------------------------
       Sorties: the flight path draws itself as you travel along it
       ---------------------------------------------------------------- */
    function initSorties() {
        var deck = $('[data-ab-flight]');
        if (!deck) return;

        var viewport = $('[data-ab-flight-viewport]', deck);
        var track = $('.ab-flight-track', deck);
        var tabs = $$('.ab-wp-btn', deck);
        var panels = $$('[data-ab-debrief]');
        var pos = $('[data-ab-flight-pos]', deck);
        var gauge = $('.ab-flight-gauge span', deck);
        var steps = $$('[data-ab-flight-step]', deck);
        if (!viewport || !track || !tabs.length) return;

        var dragged = false;

        function flown() {
            var max = viewport.scrollWidth;
            var seen = max ? (viewport.scrollLeft + viewport.clientWidth) / max : 1;
            track.style.setProperty('--flown', Math.min(1, Math.max(0, seen)).toFixed(4));
            if (gauge) gauge.style.width = (Math.min(1, Math.max(0, viewport.scrollLeft / Math.max(1, max - viewport.clientWidth))) * 100) + '%';
        }

        function centre(i) {
            var wp = tabs[i].closest('.ab-wp');
            if (!wp) return;
            var left = wp.offsetLeft + wp.offsetWidth / 2 - viewport.clientWidth / 2;
            viewport.scrollTo({ left: Math.max(0, left), behavior: AB.reduceMotion ? 'auto' : 'smooth' });
        }

        var tabset = makeTabs(tabs, panels, function (i, fromUser) {
            $$('.ab-wp', deck).forEach(function (wp, k) { wp.classList.toggle('is-selected', k === i); });
            if (pos) pos.textContent = pad2(i + 1);
            steps.forEach(function (btn) {
                var dir = parseInt(btn.getAttribute('data-ab-flight-step'), 10);
                btn.disabled = (dir < 0 && i === 0) || (dir > 0 && i === tabs.length - 1);
            });
            if (fromUser) {
                centre(i);
                var code = $('.ab-wp-code', tabs[i]);
                AB.announce('Debrief ' + (code ? code.textContent : i + 1));
            }
        }, {
            shouldIgnoreClick: function () { var was = dragged; dragged = false; return was; }
        });

        steps.forEach(function (btn) {
            btn.addEventListener('click', function () {
                tabset.select(tabset.current() + parseInt(btn.getAttribute('data-ab-flight-step'), 10), true, false);
            });
        });

        // drag to fly sideways (mouse); touch already scrolls natively
        var startX = 0, startLeft = 0, pressing = false;
        viewport.addEventListener('pointerdown', function (e) {
            if (e.pointerType !== 'mouse' || e.button !== 0) return;
            pressing = true; dragged = false;
            startX = e.clientX; startLeft = viewport.scrollLeft;
        });
        window.addEventListener('pointermove', function (e) {
            if (!pressing) return;
            var dx = e.clientX - startX;
            if (!dragged && Math.abs(dx) > 6) { dragged = true; viewport.classList.add('is-dragging'); }
            if (dragged) viewport.scrollLeft = startLeft - dx;
        });
        window.addEventListener('pointerup', function () {
            if (!pressing) return;
            pressing = false;
            viewport.classList.remove('is-dragging');
            setTimeout(function () { dragged = false; }, 0);
        });

        var ticking = false;
        viewport.addEventListener('scroll', function () {
            if (ticking) return;
            ticking = true;
            requestAnimationFrame(function () { ticking = false; flown(); });
        }, { passive: true });
        window.addEventListener('resize', flown);

        // the route draws in once, on power-up, when it is first seen
        track.classList.add('is-armed');
        AB.onPowered(function () {
            var go = function () {
                requestAnimationFrame(function () {
                    track.classList.add('is-drawn', 'is-drawing');
                    flown();
                    setTimeout(function () { track.classList.remove('is-drawing'); }, 1400);
                });
            };
            if (!('IntersectionObserver' in window)) { go(); return; }
            var io = new IntersectionObserver(function (entries) {
                if (entries[0].isIntersecting) { io.disconnect(); go(); }
            }, { threshold: 0.25 });
            io.observe(track);
        });
        AB.onModeChange(function () { setTimeout(flown, 30); });
        flown();
    }

    /* ----------------------------------------------------------------
       Ribbon rack: select a ribbon (or hover one) to read its citation
       ---------------------------------------------------------------- */
    function initRack() {
        var rack = $('[data-ab-rack]');
        if (!rack) return;
        var tabs = $$('[data-ab-ribbon]', rack);
        var panels = tabs.map(function (tab) { return document.getElementById(tab.getAttribute('aria-controls')); });
        if (!tabs.length || panels.some(function (p) { return !p; })) return;

        var tabset = makeTabs(tabs, panels, function (i, fromUser) {
            if (fromUser) AB.announce('Citation: ' + (tabs[i].getAttribute('aria-label') || ''));
        });

        if (AB.finePointer) {
            var dwell = null;
            tabs.forEach(function (tab, i) {
                tab.addEventListener('mouseenter', function () {
                    clearTimeout(dwell);
                    dwell = setTimeout(function () { if (tabset.current() !== i) tabset.select(i, false, false); }, 140);
                });
                tab.addEventListener('mouseleave', function () { clearTimeout(dwell); });
            });
        }
    }

    /* ----------------------------------------------------------------
       Commend (stars on sorties) without a page reload
       ---------------------------------------------------------------- */
    function initCommend() {
        $$('form[data-ab-commend]').forEach(function (form) {
            form.addEventListener('submit', function (e) {
                if (!window.fetch) return;
                e.preventDefault();
                var btn = $('button', form);
                if (!btn || form.getAttribute('aria-busy') === 'true') return;
                form.setAttribute('aria-busy', 'true');
                fetch(form.action, {
                    method: 'POST',
                    body: new FormData(form),
                    headers: { 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json' },
                    credentials: 'same-origin'
                }).then(function (res) {
                    var json = (res.headers.get('content-type') || '').indexOf('application/json') !== -1;
                    if (!res.ok || !json) throw new Error('fallback');
                    return res.json();
                }).then(function (data) {
                    var label = $('[data-ab-commend-label]', form);
                    var count = $('[data-ab-commend-count]', form);
                    btn.classList.toggle('is-on', data.starred);
                    btn.setAttribute('aria-pressed', String(data.starred));
                    if (label) label.textContent = data.starred ? 'Commended' : 'Commend';
                    if (count) count.textContent = pad2(data.count);
                    AB.announce(data.starred ? 'Commended' : 'Commendation withdrawn');
                }).catch(function () {
                    form.submit(); // let the server handle it the old-fashioned way
                }).then(function () { form.removeAttribute('aria-busy'); });
            });
        });
    }

    /* ----------------------------------------------------------------
       Django messages arrive as comms toasts
       ---------------------------------------------------------------- */
    function initMessages() {
        var el = document.getElementById('ab-messages');
        if (!el) return;
        var list;
        try { list = JSON.parse(el.textContent); } catch (e) { return; }
        if (!list || !list.length) return;
        var first = list[0];
        var level = (first.level || '').split(' ').pop();
        var title = level === 'success' ? 'Confirmed' : level === 'error' ? 'Alert' : 'Notice';
        var text = list.map(function (m) { return m.text; }).join(' ');
        setTimeout(function () { toast(title, text, level === 'error' ? 'error' : level === 'success' ? 'success' : 'normal'); }, 400);
    }

    /* ----------------------------------------------------------------
       "Some say…" — hover the name on the homepage
       ---------------------------------------------------------------- */
    var SOME_SAY = [
        'he refactors in his sleep. All we know is, he\'s called Evan.',
        'his commit history reads like a pre-flight checklist. All we know is, he\'s called Evan.',
        'he has never once force-pushed to main. All we know is, he\'s called Evan.',
        'his radar has never lost a target. Mostly. All we know is, he\'s called Evan.',
        'he knows every switch in a DCS cockpit by feel. All we know is, he\'s called Evan.',
        'he names his variables properly. Even the temporary ones. All we know is, he\'s called Evan.',
        'his dark mode has a dark mode. All we know is, he\'s called Evan.'
    ];
    var lastSay = -1;
    function someSay() {
        var i;
        do { i = Math.floor(Math.random() * SOME_SAY.length); } while (i === lastSay && SOME_SAY.length > 1);
        lastSay = i;
        return SOME_SAY[i];
    }

    function initSomeSay() {
        var name = $('[data-ab-somesay]');
        var box = $('.ab-somesay');
        var line = $('[data-ab-somesay-line]');
        if (!name || !box || !line) return;
        var hideTimer = null;

        function show() {
            if (!AB.classified()) return;
            clearTimeout(hideTimer);
            if (!box.classList.contains('is-on')) line.textContent = someSay();
            box.classList.add('is-on');
        }
        function hide() {
            clearTimeout(hideTimer);
            hideTimer = setTimeout(function () { box.classList.remove('is-on'); }, 900);
        }

        name.addEventListener('mouseenter', show);
        name.addEventListener('mouseleave', hide);
        name.addEventListener('click', function () {
            if (box.classList.contains('is-on')) { line.textContent = someSay(); hide(); }
            else { show(); hide(); }
        });
    }

    /* ----------------------------------------------------------------
       Night vision: N cycles off → NVG → thermal (white-hot) → off.
       Remembered for this tab only, so nobody gets stuck in green.
       ---------------------------------------------------------------- */
    var VISIONS = ['off', 'nv', 'thermal'];
    function vision() { return doc.getAttribute('data-ab-vision') || 'off'; }
    function setVision(next, quiet) {
        if (VISIONS.indexOf(next) === -1) return;
        if (next === 'off') doc.removeAttribute('data-ab-vision');
        else doc.setAttribute('data-ab-vision', next);
        AB.session('ab-vision', next);
        if (!quiet) AB.announce(next === 'nv' ? 'Night vision on' : next === 'thermal' ? 'Thermal, white hot' : 'Vision normal');
    }

    function initVision() {
        document.addEventListener('keydown', function (e) {
            if (e.key !== 'n' && e.key !== 'N') return;
            if (e.ctrlKey || e.metaKey || e.altKey || isTyping(e.target) || cmdOpen()) return;
            var next = VISIONS[(VISIONS.indexOf(vision()) + 1) % VISIONS.length];
            setVision(next);
        });
    }

    /* ----------------------------------------------------------------
       Command line (Ctrl+K)
       ---------------------------------------------------------------- */
    var cmd = null;
    function cmdOpen() { return !!(cmd && !cmd.root.hidden); }

    function initCommandLine() {
        var root = document.getElementById('ab-cmd');
        if (!root) return;
        var log = document.getElementById('ab-cmd-log');
        var form = document.getElementById('ab-cmd-form');
        var input = document.getElementById('ab-cmd-input');
        var routes = {};
        try { routes = JSON.parse(document.getElementById('ab-cmd-routes').textContent); } catch (e) { routes = {}; }

        var history = [], hIndex = 0, greeted = false, returnFocus = null;
        cmd = { root: root };

        function print(text, cls) {
            var p = document.createElement('p');
            if (cls) p.className = cls;
            p.textContent = text;
            log.appendChild(p);
            log.scrollTop = log.scrollHeight;
            return p;
        }
        function printLink(prefix, label, href) {
            var p = print(prefix ? prefix + ' ' : '', 'is-out');
            var a = document.createElement('a');
            a.href = href; a.textContent = label;
            if (/^https?:/.test(href)) { a.target = '_blank'; a.rel = 'noopener noreferrer'; }
            p.appendChild(a);
        }

        function open() {
            if (cmdOpen()) return;
            returnFocus = document.activeElement;
            root.hidden = false;
            doc.classList.add('ab-cmd-open');
            if (!greeted) {
                greeted = true;
                print('Afterburner command line. Type help for orders.', 'is-dim');
            }
            setTimeout(function () { input.focus(); }, 20);
        }
        function close() {
            if (!cmdOpen()) return;
            root.hidden = true;
            doc.classList.remove('ab-cmd-open');
            if (returnFocus && returnFocus.focus) returnFocus.focus({ preventScroll: true });
        }

        function go(page) {
            var key = (page || '').toLowerCase().replace(/^\/+|\/+$/g, '').replace(/[\s_-]+/g, '');
            if (key === '' || key === '~' || key === 'home' || key === 'base') key = 'profile';
            if (key === 'coolwall' || key === 'wall') key = 'coolwall';
            if (!routes[key]) { print('No such sector: ' + page + '. Try ls.', 'is-err'); return; }
            print('Course set for ' + key + '…', 'is-out');
            setTimeout(function () { window.location.href = routes[key]; }, 260);
        }

        function jakartaTime() {
            try {
                return new Intl.DateTimeFormat('en-GB', {
                    timeZone: 'Asia/Jakarta', weekday: 'short', day: '2-digit', month: 'short',
                    hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23'
                }).format(new Date()) + ' WIB';
            } catch (e) { return new Date().toString(); }
        }

        var COMMANDS = {
            help: function () {
                [
                    'whoami                 who flies this thing',
                    'status                 systems check',
                    'ls                     list sectors',
                    'goto <sector>          e.g. goto sorties',
                    'clearance <mode>       classified | unclassified',
                    'vision <mode>          nv | thermal | off   (or press N)',
                    'somesay                rumours',
                    'coolwall               the wall',
                    'contact                comms details',
                    'time                   Jakarta time',
                    'clear · exit'
                ].forEach(function (l) { print(l, 'is-out is-pre'); });
            },
            whoami: function () {
                print('Michael Evan Putra Nugroho. Callsign Evan.', 'is-out');
                print('Computer Science, Universitas Indonesia. Backend systems, secure by design, defence tech.', 'is-out');
            },
            status: function () {
                var user = $('.ab-overlay-user');
                print('Clearance   ' + AB.mode(), 'is-out is-pre');
                print('Vision      ' + (vision() === 'nv' ? 'night vision' : vision() === 'thermal' ? 'thermal, white hot' : 'normal'), 'is-out is-pre');
                print('Operator    ' + (user ? user.textContent : 'guest'), 'is-out is-pre');
                print('Local time  ' + jakartaTime(), 'is-out is-pre');
                print('All systems nominal.', 'is-ok');
            },
            ls: function () {
                print('profile  sorties  qualifications  ribbons  hangar  coolwall  login', 'is-out is-pre');
            },
            goto: function (args) { if (!args[0]) { print('goto where? Try ls.', 'is-err'); return; } go(args.join(' ')); },
            clearance: function (args) {
                var m = (args[0] || '').toLowerCase();
                if (m !== 'classified' && m !== 'unclassified') { print('Clearance is ' + AB.mode() + '. Use: clearance classified | unclassified', 'is-out'); return; }
                AB.setMode(m);
                print('Clearance set: ' + m + '.', 'is-ok');
            },
            vision: function (args) {
                var m = (args[0] || '').toLowerCase();
                if (m === 'nvg' || m === 'night') m = 'nv';
                if (m === 'normal' || m === 'day') m = 'off';
                if (VISIONS.indexOf(m) === -1) { print('Use: vision nv | thermal | off', 'is-err'); return; }
                setVision(m);
                print(m === 'off' ? 'Vision normal.' : m === 'nv' ? 'Night vision on. Very green.' : 'Thermal on. White hot.', 'is-ok');
            },
            somesay: function () { print('Some say ' + someSay(), 'is-out'); },
            coolwall: function () { go('coolwall'); },
            contact: function () {
                printLink('Email   ', 'michaelevanpn@gmail.com', 'mailto:michaelevanpn@gmail.com');
                printLink('GitHub  ', 'github.com/DJITOE-IPUN', 'https://github.com/DJITOE-IPUN');
                printLink('LinkedIn', 'linkedin.com/in/michael-evan-putra-nugroho-g624', 'https://www.linkedin.com/in/michael-evan-putra-nugroho-g624/');
            },
            time: function () { print(jakartaTime(), 'is-out'); },
            clear: function () { log.innerHTML = ''; },
            exit: function () { close(); },
            hello: function () { print('Loud and clear.', 'is-out'); },
            sudo: function () { print('Nice try. This incident will be reported to absolutely no one.', 'is-err'); },
            rm: function () { print('Permission denied. Also: no.', 'is-err'); },
            nv: function () { COMMANDS.vision(['nv']); },
            thermal: function () { COMMANDS.vision(['thermal']); },
            classified: function () { COMMANDS.clearance(['classified']); },
            unclassified: function () { COMMANDS.clearance(['unclassified']); }
        };
        var ALIASES = { cd: 'goto', open: 'goto', cls: 'clear', quit: 'exit', close: 'exit', hi: 'hello', date: 'time', email: 'contact', who: 'whoami', '?': 'help' };

        function run(line) {
            var raw = line.trim();
            if (!raw) return;
            print('evan@deck:~$ ' + raw, 'is-in');
            var parts = raw.split(/\s+/);
            var name = parts[0].toLowerCase();
            name = ALIASES[name] || name;
            if (COMMANDS[name]) COMMANDS[name](parts.slice(1));
            else if (routes[name.replace(/[\s_-]+/g, '')]) go(name);
            else print('Command not recognised: ' + parts[0] + '. Type help.', 'is-err');
        }

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            var value = input.value;
            if (value.trim()) { history.push(value); hIndex = history.length; }
            input.value = '';
            run(value);
        });

        input.addEventListener('keydown', function (e) {
            if (e.key === 'ArrowUp' && history.length) { e.preventDefault(); hIndex = Math.max(0, hIndex - 1); input.value = history[hIndex]; }
            else if (e.key === 'ArrowDown' && history.length) { e.preventDefault(); hIndex = Math.min(history.length, hIndex + 1); input.value = history[hIndex] || ''; }
        });

        document.addEventListener('keydown', function (e) {
            if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
                e.preventDefault();
                if (cmdOpen()) close(); else open();
                return;
            }
            if (!cmdOpen()) return;
            if (e.key === 'Escape') { e.preventDefault(); close(); return; }
            if (e.key === 'Tab') {
                var closeBtn = $('[data-ab-cmd-close]', root);
                e.preventDefault();
                (document.activeElement === input ? closeBtn : input).focus();
            }
        });

        root.addEventListener('mousedown', function (e) { if (e.target === root) close(); });
        $$('[data-ab-cmd-close]', root).forEach(function (b) { b.addEventListener('click', close); });
        $$('[data-ab-cmd-open]').forEach(function (b) { b.addEventListener('click', open); });
    }

    /* ---------------------------------------------------------------- */
    ready(function () {
        initSorties();
        initRack();
        initCommend();
        initSomeSay();
        initVision();
        initCommandLine();
        initMessages();
    });
})();
