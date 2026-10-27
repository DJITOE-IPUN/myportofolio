/* =====================================================================
   QUALIFICATIONS — the Education page, kept live over AJAX
   The server draws the first set of cards (so the page works without
   JavaScript). This script then:
   - loads the list from show_json_education and redraws it,
   - searches by institution as you type (debounced, 300 ms),
   - adds a qualification through create_education_ajax, with the
     server's field errors shown under each field.
   ===================================================================== */
(function () {
    'use strict';

    var section = document.getElementById('ratings');
    var grid = document.getElementById('education-grid');
    if (!section || !grid) return;

    var AB = window.Afterburner || { announce: function () {}, lively: function () { return false; } };
    var DUMMY = '00000000-0000-0000-0000-000000000000';
    var cfg = {
        json: section.dataset.jsonUrl,
        create: section.dataset.createUrl,
        edit: section.dataset.editUrlTemplate,
        del: section.dataset.deleteUrlTemplate
    };

    var el = {
        input: document.getElementById('search-input'),
        form: document.getElementById('education-search-form'),
        count: document.getElementById('ab-ratings-count'),
        note: document.getElementById('ab-ratings-note'),
        error: document.getElementById('error-message'),
        retry: document.getElementById('ab-ratings-retry'),
        empty: document.getElementById('ab-ratings-empty'),
        nomatch: document.getElementById('ab-ratings-nomatch'),
        nomatchTitle: document.getElementById('ab-ratings-nomatch-title'),
        modal: document.getElementById('add-education-modal'),
        createForm: document.getElementById('add-education-form'),
        scrub: document.getElementById('ab-scrub-modal'),
        scrubForm: document.getElementById('ab-scrub-form'),
        scrubName: document.getElementById('ab-scrub-name')
    };

    var abort = null, timer = null;

    function pad2(n) { return n < 10 ? '0' + n : String(n); }
    function url(template, id) { return template.replace(DUMMY, id); }
    function getCookie(name) {
        var m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
        return m ? decodeURIComponent(m[1]) : null;
    }
    function make(tag, cls, text) {
        var node = document.createElement(tag);
        if (cls) node.className = cls;
        if (text !== undefined && text !== null) node.textContent = text;
        return node;
    }
    function hide(node, hidden) { if (node) node.classList.toggle('hide', hidden); }
    function toast(title, msg, type) { if (typeof showToast === 'function') showToast(title, msg, type || 'normal', 4000); }

    /* ---------- one rating card (same markup as education.html) ---------- */
    function card(edu, perms, index) {
        var article = make('article', 'ab-rating is-inview' + (edu.ongoing ? ' is-training' : ''));
        article.style.setProperty('--d', (index * 60) + 'ms');
        var inner = make('div', 'ab-rating-inner');

        var top = make('header', 'ab-rating-top');
        top.appendChild(make('span', 'ab-rating-code', edu.code));
        top.appendChild(make('span', 'ab-rating-class', edu.rating));
        inner.appendChild(top);

        inner.appendChild(make('h3', 'ab-rating-inst', edu.institution));
        inner.appendChild(make('p', 'ab-rating-field', edu.field_of_study));

        var facts = make('div', 'ab-rating-facts');
        var dl = make('dl');
        [['Period', edu.date_range], ['Level', edu.degree]].forEach(function (pair) {
            var d = make('div');
            d.appendChild(make('dt', null, pair[0]));
            d.appendChild(make('dd', null, pair[1]));
            dl.appendChild(d);
        });
        facts.appendChild(dl);
        facts.appendChild(make('p', 'ab-stamp' + (edu.ongoing ? ' is-training' : ''), edu.status));
        inner.appendChild(facts);

        if (edu.semesters) {
            var prog = make('div', 'ab-rating-progress');
            prog.setAttribute('role', 'img');
            prog.setAttribute('aria-label', edu.semester ? 'Semester ' + edu.semester + ' of ' + edu.semesters
                : (edu.ongoing ? 'In training' : 'All ' + edu.semesters + ' semesters complete'));
            var label = make('p', 'ab-rating-progress-label');
            label.appendChild(make('span', null, edu.semester ? 'Semester ' + pad2(edu.semester) + ' of ' + pad2(edu.semesters) : (edu.ongoing ? 'In progress' : 'Complete')));
            label.appendChild(make('span', null, edu.progress === null || edu.progress === undefined ? '—' : edu.progress + '%'));
            prog.appendChild(label);
            var ol = make('ol', 'ab-rating-segments');
            ol.style.setProperty('--segments', edu.semesters);
            ol.setAttribute('aria-hidden', 'true');
            for (var i = 1; i <= edu.semesters; i++) {
                var cls = !edu.ongoing ? 'is-done' : (edu.semester && i < edu.semester ? 'is-done' : (edu.semester && i === edu.semester ? 'is-now' : ''));
                ol.appendChild(make('li', cls));
            }
            prog.appendChild(ol);
            inner.appendChild(prog);
        }

        if (edu.description) inner.appendChild(make('p', 'ab-rating-notes', edu.description));

        if (perms.is_editor || perms.is_superuser) {
            var foot = make('footer', 'ab-rating-maint');
            if (perms.is_editor) {
                var edit = make('a', 'ab-btn ab-btn-quiet', 'Edit');
                edit.href = url(cfg.edit, edu.id);
                edit.setAttribute('aria-label', 'Edit ' + edu.institution);
                foot.appendChild(edit);
            }
            if (perms.is_superuser && el.scrub) {
                var del = make('button', 'ab-btn ab-btn-quiet ab-btn-danger', 'Scrub');
                del.type = 'button';
                del.setAttribute('aria-label', 'Delete ' + edu.institution);
                del.addEventListener('click', function () {
                    el.scrubForm.action = url(cfg.del, edu.id);
                    el.scrubName.textContent = edu.institution;
                    el.scrub.showPopover();
                });
                foot.appendChild(del);
            }
            inner.appendChild(foot);
        }

        article.appendChild(inner);
        return article;
    }

    function setStat(label, value) {
        document.querySelectorAll('.ab-pagestats div').forEach(function (d) {
            var dt = d.querySelector('dt');
            if (dt && dt.textContent.trim().toLowerCase() === label) d.querySelector('dd').textContent = value;
        });
    }

    /* ---------- load + render ---------- */
    function load(query) {
        if (abort) abort.abort();
        abort = 'AbortController' in window ? new AbortController() : null;
        el.note.textContent = 'Scanning…';
        grid.setAttribute('aria-busy', 'true');

        fetch(cfg.json + '?institution=' + encodeURIComponent(query || ''), {
            headers: { 'Accept': 'application/json' },
            credentials: 'same-origin',
            signal: abort ? abort.signal : undefined
        }).then(function (res) {
            if (!res.ok) throw new Error('HTTP ' + res.status);
            return res.json();
        }).then(function (data) {
            var list = data.educations || [];
            var perms = data.user_permissions || {};
            grid.innerHTML = '';
            list.forEach(function (edu, i) { grid.appendChild(card(edu, perms, i)); });

            hide(el.error, true);
            hide(grid, !list.length);
            hide(el.empty, !!(list.length || query));
            hide(el.nomatch, !!(list.length || !query));
            if (!list.length && query) el.nomatchTitle.textContent = 'No institution matches “' + query + '”.';

            el.count.textContent = query ? pad2(list.length) + (list.length === 1 ? ' match' : ' matches') : pad2(list.length) + ' on file';
            el.note.textContent = query ? 'Filtered' : pad2(list.length) + ' on file';
            if (!query) {
                setStat('ratings', pad2(list.length));
                setStat('in training', pad2(list.filter(function (e) { return e.ongoing; }).length));
            }
        }).catch(function (err) {
            if (err && err.name === 'AbortError') return;
            console.error('Qualifications: could not load', err);
            hide(el.error, false);
            el.note.textContent = 'No link';
            toast('Alert', 'Couldn’t load the qualifications.', 'error');
        }).then(function () { grid.removeAttribute('aria-busy'); });
    }

    if (el.input) {
        el.input.addEventListener('input', function () {
            clearTimeout(timer);
            timer = setTimeout(function () { load(el.input.value.trim()); }, 300);
        });
    }
    if (el.form) el.form.addEventListener('submit', function (e) { e.preventDefault(); clearTimeout(timer); load(el.input.value.trim()); });
    if (el.retry) el.retry.addEventListener('click', function () { load(el.input ? el.input.value.trim() : ''); });

    /* ---------- add qualification (AJAX) ---------- */
    function clearErrors(form) {
        form.querySelectorAll('[data-ab-error-for]').forEach(function (p) { p.textContent = ''; p.hidden = true; });
        form.querySelectorAll('.ab-field.has-error').forEach(function (f) { f.classList.remove('has-error'); });
    }

    function showErrors(form, errors) {
        Object.keys(errors || {}).forEach(function (name) {
            var messages = [].concat(errors[name]).map(function (m) { return typeof m === 'string' ? m : (m && m.message) || ''; });
            var slot = form.querySelector('[data-ab-error-for="' + name + '"]');
            if (slot) {
                slot.textContent = messages.join(' ');
                slot.hidden = false;
                slot.closest('.ab-field').classList.add('has-error');
            }
        });
        var first = form.querySelector('.ab-field.has-error input, .ab-field.has-error select, .ab-field.has-error textarea');
        if (first) first.focus();
    }

    if (el.createForm && cfg.create) {
        if (el.modal) el.modal.addEventListener('toggle', function (e) {
            if (e.newState === 'open') {
                var first = el.createForm.querySelector('input, select, textarea');
                if (first) setTimeout(function () { first.focus(); }, 30);
            } else { clearErrors(el.createForm); }
        });

        el.createForm.addEventListener('submit', function (e) {
            e.preventDefault();
            var submit = el.createForm.querySelector('button[type="submit"]');
            if (submit.getAttribute('aria-busy') === 'true') return;
            submit.setAttribute('aria-busy', 'true');
            submit.textContent = 'Logging…';
            clearErrors(el.createForm);

            fetch(cfg.create, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken'), 'X-Requested-With': 'XMLHttpRequest' },
                body: new FormData(el.createForm),
                credentials: 'same-origin'
            }).then(function (res) {
                return res.json().catch(function () { return {}; }).then(function (data) { return { res: res, data: data }; });
            }).then(function (r) {
                if (r.res.status === 201) {
                    el.createForm.reset();
                    if (el.modal && el.modal.hidePopover) el.modal.hidePopover();
                    toast('Confirmed', r.data.message || 'Qualification added.', 'success');
                    if (el.input) el.input.value = '';
                    load('');
                } else {
                    if (r.data.errors) showErrors(el.createForm, r.data.errors);
                    toast('Not logged', r.data.error || 'Something went wrong (status ' + r.res.status + ').', 'error');
                }
            }).catch(function () {
                toast('Not logged', 'Couldn’t reach the server. Try again.', 'error');
            }).then(function () {
                submit.removeAttribute('aria-busy');
                submit.textContent = 'Log rating';
            });
        });
    }

    load('');
})();
