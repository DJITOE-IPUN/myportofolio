/* =====================================================================
   HANGAR — the Projects page
   Loads projects over AJAX (show_json_projects, which also says what the
   visitor may do), live search, filter by system, commend without a
   reload, commission over AJAX (create_project_ajax) with field errors
   under each field, and a styled scrap confirmation.
   ===================================================================== */
(function () {
    'use strict';

    var section = document.getElementById('projects');
    if (!section) return;

    var AB = window.Afterburner || { announce: function () {}, lively: function () { return false; } };
    var DUMMY = '00000000-0000-0000-0000-000000000000';
    var cfg = {
        json: section.dataset.jsonUrl,
        create: section.dataset.createUrl,
        star: section.dataset.starUrlTemplate,
        edit: section.dataset.editUrlTemplate,
        del: section.dataset.deleteUrlTemplate,
        login: section.dataset.loginUrl,
        isAuth: section.dataset.isAuth === 'true',
        isEditor: section.dataset.isEditor === 'true',
        isSuperuser: section.dataset.isSuperuser === 'true'
    };

    var el = {
        loading: document.getElementById('loading'),
        error: document.getElementById('error'),
        empty: document.getElementById('empty'),
        grid: document.getElementById('grid'),
        form: document.getElementById('project-search-form'),
        input: document.getElementById('search-input'),
        count: document.getElementById('ab-hangar-count'),
        note: document.getElementById('ab-hangar-note'),
        filter: document.getElementById('ab-hangar-filter'),
        filterName: document.getElementById('ab-hangar-filter-name'),
        filterClear: document.getElementById('ab-hangar-filter-clear'),
        retry: document.getElementById('ab-hangar-retry'),
        emptyCode: document.getElementById('ab-hangar-empty-code'),
        emptyTitle: document.getElementById('ab-hangar-empty-title'),
        emptyNote: document.getElementById('ab-hangar-empty-note'),
        createForm: document.getElementById('project-form'),
        createModal: document.getElementById('add-project-modal'),
        scrapModal: document.getElementById('ab-scrap-modal'),
        scrapForm: document.getElementById('ab-scrap-form'),
        scrapName: document.getElementById('ab-scrap-name')
    };

    var projects = [];       // last response from the server (already filtered by title)
    var systemFilter = '';   // client-side filter by one tech-stack item
    var abort = null;
    var debounce = null;
    var csrf = (document.querySelector('#csrf-token-form [name=csrfmiddlewaretoken]') || {}).value || getCookie('csrftoken');

    function getCookie(name) {
        var match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
        return match ? decodeURIComponent(match[1]) : null;
    }

    function pad2(n) { return n < 10 ? '0' + n : String(n); }
    function url(template, id) { return template.replace(DUMMY, id); }
    function systemsOf(p) { return (p.fields.tech_stack || '').split(',').map(function (s) { return s.trim(); }).filter(Boolean); }

    function make(tag, cls, text) {
        var node = document.createElement(tag);
        if (cls) node.className = cls;
        if (text !== undefined && text !== null) node.textContent = text;
        return node;
    }

    function svg(tag, attrs) {
        var node = document.createElementNS('http://www.w3.org/2000/svg', tag);
        Object.keys(attrs || {}).forEach(function (k) { node.setAttribute(k, attrs[k]); });
        return node;
    }

    var STAR = 'M8 1.8 9.9 5.9l4.4.5-3.3 3 .9 4.4L8 11.6 4.1 13.8 5 9.4 1.7 6.4l4.4-.5Z';
    function starIcon() {
        var s = svg('svg', { viewBox: '0 0 16 16', 'aria-hidden': 'true' });
        s.appendChild(svg('path', { d: STAR }));
        return s;
    }

    /* ---------- states ---------- */
    function show(state) {
        el.loading.classList.toggle('hide', state !== 'loading');
        el.error.classList.toggle('hide', state !== 'error');
        el.empty.classList.toggle('hide', state !== 'empty');
        el.grid.classList.toggle('hide', state !== 'grid');
    }

    /* ---------- the generated blueprint for bays without an image ---------- */
    function blueprint(title) {
        var initials = (title || '?').split(/\s+/).filter(Boolean).slice(0, 2).map(function (w) { return w[0]; }).join('').toUpperCase() || '?';
        var s = svg('svg', { class: 'ab-bay-blueprint', viewBox: '0 0 320 180', preserveAspectRatio: 'xMidYMid slice', 'aria-hidden': 'true' });
        for (var x = 20; x < 320; x += 20) s.appendChild(svg('line', { x1: x, y1: 0, x2: x, y2: 180, class: x % 80 === 0 ? 'bp-major' : 'bp-minor' }));
        for (var y = 20; y < 180; y += 20) s.appendChild(svg('line', { x1: 0, y1: y, x2: 320, y2: y, class: y % 80 === 0 ? 'bp-major' : 'bp-minor' }));
        s.appendChild(svg('circle', { cx: 160, cy: 90, r: 58, class: 'bp-line' }));
        s.appendChild(svg('line', { x1: 60, y1: 90, x2: 260, y2: 90, class: 'bp-dash' }));
        s.appendChild(svg('line', { x1: 160, y1: 18, x2: 160, y2: 162, class: 'bp-dash' }));
        var t = svg('text', { x: 160, y: 104, 'text-anchor': 'middle', class: 'bp-text' });
        t.textContent = initials;
        s.appendChild(t);
        var c = svg('text', { x: 26, y: 160, class: 'bp-caption' });
        c.textContent = 'NO IMAGE · BLUEPRINT';
        s.appendChild(c);
        return s;
    }

    /* ---------- one bay ---------- */
    function bay(item, index) {
        var p = item.fields, id = item.pk;
        var article = make('article', 'ab-bay');
        article.style.setProperty('--i', index);

        var head = make('header', 'ab-bay-head');
        head.appendChild(make('span', null, 'Bay ' + pad2(index + 1)));
        head.appendChild(make('span', 'ab-dim', 'AF-' + String(id).slice(0, 4).toUpperCase()));
        article.appendChild(head);

        var visual = make('div', 'ab-bay-visual');
        if (p.project_image_url) {
            var img = make('img');
            img.src = p.project_image_url;
            img.alt = 'Screenshot of ' + p.title;
            img.loading = 'lazy';
            img.addEventListener('error', function () { img.replaceWith(blueprint(p.title)); });
            visual.appendChild(img);
        } else {
            visual.appendChild(blueprint(p.title));
        }
        article.appendChild(visual);

        var body = make('div', 'ab-bay-body');
        body.appendChild(make('h3', 'ab-bay-title', p.title));
        if (p.description) body.appendChild(make('p', 'ab-bay-desc', p.description));
        var systems = systemsOf(item);
        if (systems.length) {
            var list = make('ul', 'ab-bay-systems');
            list.setAttribute('aria-label', 'Systems');
            systems.forEach(function (name) {
                var li = make('li');
                var chip = make('button', 'ab-bay-chip' + (systemFilter && name.toLowerCase() === systemFilter.toLowerCase() ? ' is-on' : ''), name);
                chip.type = 'button';
                chip.title = 'Show only projects using ' + name;
                chip.addEventListener('click', function () { setFilter(name); });
                li.appendChild(chip);
                list.appendChild(li);
            });
            body.appendChild(list);
        }
        article.appendChild(body);

        var foot = make('footer', 'ab-bay-actions');
        if (p.project_url) {
            var inspect = make('a', 'ab-btn ab-btn-solid', 'Inspect');
            inspect.href = p.project_url;
            inspect.target = '_blank';
            inspect.rel = 'noopener noreferrer';
            inspect.setAttribute('aria-label', 'Inspect ' + p.title + ' (opens in a new tab)');
            foot.appendChild(inspect);
        }

        var commend;
        if (cfg.isAuth) {
            commend = make('button', 'ab-commend' + (p.is_starred ? ' is-on' : ''));
            commend.type = 'button';
            commend.setAttribute('aria-pressed', String(!!p.is_starred));
            commend.addEventListener('click', function () { toggleStar(item, commend); });
        } else {
            commend = make('a', 'ab-commend');
            commend.href = cfg.login;
            commend.title = 'Sign in to commend';
        }
        commend.appendChild(starIcon());
        commend.appendChild(make('span', 'ab-commend-label', cfg.isAuth ? (p.is_starred ? 'Commended' : 'Commend') : 'Commend'));
        commend.appendChild(make('span', 'ab-commend-count', pad2(p.star_count || 0)));
        if (p.star_count) commend.title = 'Commended by ' + p.starred_by_names;
        foot.appendChild(commend);

        if (cfg.isEditor || cfg.isSuperuser) {
            var maint = make('span', 'ab-bay-maint');
            if (cfg.isEditor) {
                var edit = make('a', 'ab-btn ab-btn-quiet', 'Refit');
                edit.href = url(cfg.edit, id);
                edit.setAttribute('aria-label', 'Edit ' + p.title);
                maint.appendChild(edit);
            }
            if (cfg.isSuperuser && el.scrapModal) {
                var scrap = make('button', 'ab-btn ab-btn-quiet ab-btn-danger', 'Scrap');
                scrap.type = 'button';
                scrap.setAttribute('aria-label', 'Delete ' + p.title);
                scrap.addEventListener('click', function () { openScrap(item); });
                maint.appendChild(scrap);
            }
            foot.appendChild(maint);
        }
        article.appendChild(foot);
        return article;
    }

    /* ---------- render ---------- */
    function render() {
        var query = el.input.value.trim();
        var visible = systemFilter
            ? projects.filter(function (p) { return systemsOf(p).some(function (s) { return s.toLowerCase() === systemFilter.toLowerCase(); }); })
            : projects;

        // header readouts describe the whole hangar as the server returned it
        var allSystems = {};
        var stars = 0;
        projects.forEach(function (p) {
            systemsOf(p).forEach(function (s) { allSystems[s.toLowerCase()] = true; });
            stars += p.fields.star_count || 0;
        });
        setStat('airframes', pad2(projects.length));
        setStat('systems', pad2(Object.keys(allSystems).length));
        setStat('stars', pad2(stars));

        el.filter.hidden = !systemFilter;
        if (systemFilter) el.filterName.textContent = systemFilter;

        var filtered = !!(query || systemFilter);
        el.count.textContent = filtered
            ? pad2(visible.length) + (visible.length === 1 ? ' match' : ' matches')
            : pad2(visible.length) + (visible.length === 1 ? ' airframe' : ' airframes');

        if (!visible.length) {
            if (filtered) {
                el.emptyCode.textContent = 'No contact';
                el.emptyTitle.textContent = 'Nothing in the hangar matches ' + (query ? '“' + query + '”' : '') + (query && systemFilter ? ' on ' : '') + (systemFilter ? systemFilter : '') + '.';
                el.emptyNote.textContent = 'Try a shorter name, or clear the filter.';
            } else {
                el.emptyCode.textContent = 'Hangar empty';
                el.emptyTitle.textContent = 'No projects in the hangar yet.';
                el.emptyNote.textContent = 'Suspiciously tidy in here.';
            }
            show('empty');
            el.note.textContent = filtered ? 'No contact' : 'Hangar empty';
            return;
        }

        el.grid.innerHTML = '';
        el.grid.classList.toggle('is-entering', !!AB.lively());
        visible.forEach(function (item, i) { el.grid.appendChild(bay(item, projects.indexOf(item))); });
        show('grid');
        el.note.textContent = filtered ? 'Filtered' : 'Live from the hangar';
    }

    function setStat(name, value) {
        var node = document.querySelector('[data-ab-hangar-stat="' + name + '"]');
        if (node) node.textContent = value;
    }

    function setFilter(name) {
        systemFilter = systemFilter && systemFilter.toLowerCase() === name.toLowerCase() ? '' : name;
        render();
        AB.announce(systemFilter ? 'Showing projects using ' + systemFilter : 'Filter cleared');
    }

    /* ---------- accept both JSON shapes ----------
       show_json_projects: { projects: [{id, title, …, total_stars, is_starred}], user_permissions }
       get_projects_json:  [{pk, fields: {title, …, star_count, is_starred, starred_by_names}}] */
    function normalise(data) {
        if (Array.isArray(data)) return data;
        var perms = data && data.user_permissions;
        if (perms) {
            cfg.isAuth = !!perms.is_authenticated;
            cfg.isEditor = !!perms.is_editor;
            cfg.isSuperuser = !!perms.is_superuser;
        }
        return ((data && data.projects) || []).map(function (p) {
            return {
                pk: p.id,
                fields: {
                    title: p.title,
                    description: p.description,
                    tech_stack: p.tech_stack,
                    project_url: p.project_url,
                    project_image_url: p.project_image_url,
                    star_count: p.total_stars || 0,
                    is_starred: !!p.is_starred,
                    starred_by_names: p.starred_by_names || ''
                }
            };
        });
    }

    /* ---------- load ---------- */
    function load(query) {
        if (abort) abort.abort();
        abort = 'AbortController' in window ? new AbortController() : null;
        if (!el.grid.children.length) show('loading');
        el.note.textContent = 'Scanning…';

        var target = cfg.json + '?title=' + encodeURIComponent(query || '');
        fetch(target, { headers: { 'Accept': 'application/json' }, signal: abort ? abort.signal : undefined, credentials: 'same-origin' })
            .then(function (res) { if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); })
            .then(function (data) {
                projects = normalise(data);
                render();
            })
            .catch(function (err) {
                if (err && err.name === 'AbortError') return;
                console.error('Hangar: could not load projects', err);
                show('error');
                el.note.textContent = 'No link';
            });

        // keep the address bar in step with the search, without reloading
        try {
            var u = new URL(window.location.href);
            if (query) u.searchParams.set('title', query); else u.searchParams.delete('title');
            history.replaceState(null, '', u.pathname + u.search + u.hash);
        } catch (e) { /* old browser: fine */ }
    }

    el.input.addEventListener('input', function () {
        clearTimeout(debounce);
        debounce = setTimeout(function () { load(el.input.value.trim()); }, 300);
    });
    el.form.addEventListener('submit', function (e) {
        e.preventDefault();
        clearTimeout(debounce);
        load(el.input.value.trim());
    });
    if (el.filterClear) el.filterClear.addEventListener('click', function () { setFilter(systemFilter); });
    if (el.retry) el.retry.addEventListener('click', function () { load(el.input.value.trim()); });

    /* ---------- commend ---------- */
    function toggleStar(item, btn) {
        if (btn.getAttribute('aria-busy') === 'true') return;
        btn.setAttribute('aria-busy', 'true');
        var body = new FormData();
        body.append('csrfmiddlewaretoken', csrf);
        fetch(url(cfg.star, item.pk), {
            method: 'POST',
            body: body,
            headers: { 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json', 'X-CSRFToken': csrf },
            credentials: 'same-origin'
        }).then(function (res) {
            if (!res.ok || (res.headers.get('content-type') || '').indexOf('application/json') === -1) throw new Error('HTTP ' + res.status);
            return res.json();
        }).then(function (data) {
            item.fields.is_starred = data.starred;
            item.fields.star_count = data.count;
            btn.classList.toggle('is-on', data.starred);
            btn.setAttribute('aria-pressed', String(data.starred));
            btn.querySelector('.ab-commend-label').textContent = data.starred ? 'Commended' : 'Commend';
            btn.querySelector('.ab-commend-count').textContent = pad2(data.count);
            var total = projects.reduce(function (sum, p) { return sum + (p.fields.star_count || 0); }, 0);
            setStat('stars', pad2(total));
            AB.announce(data.starred ? 'Commended ' + item.fields.title : 'Commendation withdrawn');
        }).catch(function () {
            if (typeof showToast === 'function') showToast('Alert', 'That commendation didn’t get through. Try again.', 'error');
        }).then(function () { btn.removeAttribute('aria-busy'); });
    }

    /* ---------- scrap ---------- */
    function openScrap(item) {
        el.scrapForm.action = url(cfg.del, item.pk);
        el.scrapName.textContent = item.fields.title;
        if (el.scrapModal.showPopover) el.scrapModal.showPopover();
        else if (window.confirm('Scrap ' + item.fields.title + '?')) el.scrapForm.submit();
    }

    /* ---------- commission (AJAX create) ---------- */
    if (el.createForm && cfg.create) {
        function clearErrors() {
            el.createForm.querySelectorAll('[data-ab-error-for]').forEach(function (p) { p.textContent = ''; p.hidden = true; });
            el.createForm.querySelectorAll('.ab-field.has-error').forEach(function (f) { f.classList.remove('has-error'); });
        }
        if (el.createModal) el.createModal.addEventListener('toggle', function (e) { if (e.newState !== 'open') clearErrors(); });

        el.createForm.addEventListener('submit', function (e) {
            e.preventDefault();
            var submit = el.createForm.querySelector('button[type="submit"]');
            submit.disabled = true;
            clearErrors();
            fetch(cfg.create, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') || csrf },
                body: new FormData(el.createForm),
                credentials: 'same-origin'
            }).then(function (res) {
                return res.json().catch(function () { return {}; }).then(function (result) { return { res: res, result: result }; });
            }).then(function (r) {
                if (r.res.ok) {
                    el.createForm.reset();
                    if (el.createModal && el.createModal.hidePopover) el.createModal.hidePopover();
                    if (typeof showToast === 'function') showToast('Confirmed', r.result.message || 'Airframe commissioned. It’s in the hangar.', 'success');
                    load(el.input.value.trim());
                } else {
                    // errors arrive as {field: ["message", …]} (form.errors) or {field: [{message}]}
                    var errors = r.result.errors || {};
                    Object.keys(errors).forEach(function (name) {
                        var text = [].concat(errors[name]).map(function (m) { return typeof m === 'string' ? m : (m && m.message) || ''; }).join(' ');
                        var slot = el.createForm.querySelector('[data-ab-error-for="' + name + '"]');
                        if (slot) { slot.textContent = text; slot.hidden = false; slot.closest('.ab-field').classList.add('has-error'); }
                    });
                    var first = el.createForm.querySelector('.ab-field.has-error input, .ab-field.has-error textarea');
                    if (first) first.focus();
                    if (typeof showToast === 'function') showToast('Commission failed', r.result.error || r.result.message || 'Something went wrong (status ' + r.res.status + ').', 'error', 5000);
                }
            }).catch(function () {
                if (typeof showToast === 'function') showToast('Commission failed', 'Couldn’t reach the server. Try again.', 'error');
            }).then(function () { submit.disabled = false; });
        });
    }

    load(el.input.value.trim());
})();
