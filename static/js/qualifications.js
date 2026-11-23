/* =====================================================================
   QUALIFICATIONS — the Education page, kept live over the REST API
   The server draws the first set of cards (so the page works without
   JavaScript). This script then talks to Django REST Framework (Tugas 6):
     GET    /api/v1/education/?institution=…   list + search (debounced, 300 ms)
     POST   /api/v1/education/                 add (JSON body)          owner
     PATCH  /api/v1/education/<id>/            amend changed fields     Editor, owner
     DELETE /api/v1/education/<id>/            scrub (204, no body)     owner
     POST   /api/v1/education/<id>/star/       endorse toggle           any account
   Every write carries X-CSRFToken. DRF's 400 field errors land under each
   field, and every 400/403 message is shown in a toast. Text from the API
   only ever reaches the page through textContent, so it is never parsed as
   HTML. Which buttons appear comes from the template; the API's permission
   class has the final say.
   ===================================================================== */
(function () {
    'use strict';

    var section = document.getElementById('ratings');
    var grid = document.getElementById('education-grid');
    if (!section || !grid) return;

    var AB = window.Afterburner || { announce: function () {}, lively: function () { return false; } };
    var DUMMY = '00000000-0000-0000-0000-000000000000';
    var STAR = 'M8 1.8 9.9 5.9l4.4.5-3.3 3 .9 4.4L8 11.6 4.1 13.8 5 9.4 1.7 6.4l4.4-.5Z';
    var FIELDS = ['institution', 'degree', 'field_of_study', 'date_range', 'description'];
    var cfg = {
        list: section.dataset.listUrl,
        detail: section.dataset.detailUrlTemplate,
        star: section.dataset.starUrlTemplate,
        edit: section.dataset.editUrlTemplate,   // no-JS fallback (Tugas 3 edit page)
        del: section.dataset.deleteUrlTemplate,  // no-JS fallback for the scrub form
        login: section.dataset.loginUrl,
        isAuth: section.dataset.isAuth === 'true',
        isEditor: section.dataset.isEditor === 'true',
        isSuperuser: section.dataset.isSuperuser === 'true'
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
        editModal: document.getElementById('edit-education-modal'),
        editForm: document.getElementById('edit-education-form'),
        editCode: document.getElementById('edit-education-code'),
        scrub: document.getElementById('ab-scrub-modal'),
        scrubForm: document.getElementById('ab-scrub-form'),
        scrubName: document.getElementById('ab-scrub-name')
    };

    var records = [];  // last list from the API
    var abort = null, timer = null;

    /* ---------- small helpers ---------- */
    function pad2(n) { return n < 10 ? '0' + n : String(n); }
    function url(template, id) { return template.replace(DUMMY, id); }
    function getCookie(name) {
        var m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
        return m ? decodeURIComponent(m[1]) : null;
    }
    // The cookie is the source of truth; the hidden {% csrf_token %} form only makes sure it exists.
    function csrfToken() {
        return getCookie('csrftoken') || (document.querySelector('#csrf-token-form [name=csrfmiddlewaretoken]') || {}).value || '';
    }
    // Every node is built with textContent: API text is never parsed as HTML (XSS-safe by construction).
    function make(tag, cls, text) {
        var node = document.createElement(tag);
        if (cls) node.className = cls;
        if (text !== undefined && text !== null) node.textContent = text;
        return node;
    }
    function starIcon() {
        var ns = 'http://www.w3.org/2000/svg';
        var s = document.createElementNS(ns, 'svg');
        s.setAttribute('viewBox', '0 0 16 16');
        s.setAttribute('aria-hidden', 'true');
        var path = document.createElementNS(ns, 'path');
        path.setAttribute('d', STAR);
        s.appendChild(path);
        return s;
    }
    function hide(node, hidden) { if (node) node.classList.toggle('hide', hidden); }
    function toast(title, msg, type, ms) { if (typeof showToast === 'function') showToast(title, msg, type || 'normal', ms || 4000); }

    /* ---------- one place for every write (POST / PATCH / DELETE) ----------
       Sends JSON with the CSRF token and returns the parsed body (null for 204).
       Throws an Error with .status, and .fields holding DRF's per-field messages. */
    function apiErrorMessage(data, status) {
        if (data && typeof data.detail === 'string') return data.detail;  // 403 / 404 / 405
        var messages = [];
        Object.keys(data || {}).forEach(function (k) {
            [].concat(data[k]).forEach(function (m) { if (typeof m === 'string') messages.push(m); });
        });
        return messages.join(' ') || 'Request failed (HTTP ' + status + ').';
    }

    function api(target, method, payload) {
        return fetch(target, {
            method: method,
            headers: { 'Accept': 'application/json', 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
            body: payload === undefined ? undefined : JSON.stringify(payload),
            credentials: 'same-origin'
        }).then(function (res) {
            if (res.status === 204) return null;
            return res.json().catch(function () { return {}; }).then(function (data) {
                if (!res.ok) {
                    var err = new Error(apiErrorMessage(data, res.status));
                    err.status = res.status;
                    err.fields = data && typeof data.detail !== 'string' ? data : {};
                    throw err;
                }
                return data;
            });
        });
    }

    // Toast titles per status, so a 400 reads differently from a 403
    function failToast(action, err) {
        if (!err.status) return toast(action + ' failed', 'Couldn’t reach the server. Try again.', 'error');
        var title = err.status === 403 ? 'Clearance insufficient' : (err.status === 400 ? 'Check the fields' : action + ' failed');
        toast(title, err.message, 'error', 5000);
    }

    /* ---------- one rating card (same markup as education.html) ---------- */
    function card(edu, index) {
        var q = edu.qualification || {};
        var article = make('article', 'ab-rating is-inview' + (q.ongoing ? ' is-training' : ''));
        article.style.setProperty('--d', (index * 60) + 'ms');
        var inner = make('div', 'ab-rating-inner');

        var top = make('header', 'ab-rating-top');
        top.appendChild(make('span', 'ab-rating-code', q.code));
        top.appendChild(make('span', 'ab-rating-class', q.rating));
        inner.appendChild(top);

        inner.appendChild(make('h3', 'ab-rating-inst', edu.institution));
        inner.appendChild(make('p', 'ab-rating-field', edu.field_of_study));

        var facts = make('div', 'ab-rating-facts');
        var dl = make('dl');
        [['Period', edu.date_range], ['Level', edu.degree_display]].forEach(function (pair) {
            var d = make('div');
            d.appendChild(make('dt', null, pair[0]));
            d.appendChild(make('dd', null, pair[1]));
            dl.appendChild(d);
        });
        facts.appendChild(dl);
        facts.appendChild(make('p', 'ab-stamp' + (q.ongoing ? ' is-training' : ''), q.status));
        inner.appendChild(facts);

        if (q.semesters) {
            var prog = make('div', 'ab-rating-progress');
            prog.setAttribute('role', 'img');
            prog.setAttribute('aria-label', q.semester ? 'Semester ' + q.semester + ' of ' + q.semesters
                : (q.ongoing ? 'In training' : 'All ' + q.semesters + ' semesters complete'));
            var label = make('p', 'ab-rating-progress-label');
            label.appendChild(make('span', null, q.semester ? 'Semester ' + pad2(q.semester) + ' of ' + pad2(q.semesters) : (q.ongoing ? 'In progress' : 'Complete')));
            label.appendChild(make('span', null, q.progress === null || q.progress === undefined ? '—' : q.progress + '%'));
            prog.appendChild(label);
            var ol = make('ol', 'ab-rating-segments');
            ol.style.setProperty('--segments', q.semesters);
            ol.setAttribute('aria-hidden', 'true');
            for (var i = 1; i <= q.semesters; i++) {
                var cls = !q.ongoing ? 'is-done' : (q.semester && i < q.semester ? 'is-done' : (q.semester && i === q.semester ? 'is-now' : ''));
                ol.appendChild(make('li', cls));
            }
            prog.appendChild(ol);
            inner.appendChild(prog);
        }

        if (edu.description) inner.appendChild(make('p', 'ab-rating-notes', edu.description));

        var foot = make('footer', 'ab-rating-actions');
        foot.appendChild(endorseButton(edu));

        if (cfg.isEditor) {  // is_editor is true for Editors and the owner
            var maint = make('span', 'ab-rating-maint');
            var edit = make('button', 'ab-btn ab-btn-quiet', 'Edit');
            edit.type = 'button';
            edit.setAttribute('aria-label', 'Edit ' + edu.institution);
            edit.addEventListener('click', function () { openEdit(edu); });
            maint.appendChild(edit);
            if (cfg.isSuperuser && el.scrub) {
                var del = make('button', 'ab-btn ab-btn-quiet ab-btn-danger', 'Scrub');
                del.type = 'button';
                del.setAttribute('aria-label', 'Delete ' + edu.institution);
                del.addEventListener('click', function () { openScrub(edu); });
                maint.appendChild(del);
            }
            foot.appendChild(maint);
        }
        inner.appendChild(foot);

        article.appendChild(inner);
        return article;
    }

    function endorseButton(edu) {
        var btn;
        if (cfg.isAuth) {
            btn = make('button', 'ab-commend' + (edu.is_starred ? ' is-on' : ''));
            btn.type = 'button';
            btn.setAttribute('aria-pressed', String(!!edu.is_starred));
            btn.addEventListener('click', function () { toggleStar(edu, btn); });
        } else {
            btn = make('a', 'ab-commend');
            btn.href = cfg.login;
            btn.title = 'Sign in to endorse';
        }
        btn.appendChild(starIcon());
        btn.appendChild(make('span', 'ab-commend-label', edu.is_starred ? 'Endorsed' : 'Endorse'));
        btn.appendChild(make('span', 'ab-commend-count', pad2(edu.star_count || 0)));
        return btn;
    }

    function setStat(label, value) {
        document.querySelectorAll('.ab-pagestats div').forEach(function (d) {
            var dt = d.querySelector('dt');
            if (dt && dt.textContent.trim().toLowerCase() === label) d.querySelector('dd').textContent = value;
        });
    }

    /* ---------- load + render (GET /api/v1/education/?institution=…) ---------- */
    function currentQuery() { return el.input ? el.input.value.trim() : ''; }

    function render(query) {
        grid.innerHTML = '';
        records.forEach(function (edu, i) { grid.appendChild(card(edu, i)); });

        hide(el.error, true);
        hide(grid, !records.length);
        hide(el.empty, !!(records.length || query));
        hide(el.nomatch, !!(records.length || !query));
        if (!records.length && query) el.nomatchTitle.textContent = 'No institution matches “' + query + '”.';

        el.count.textContent = query ? pad2(records.length) + (records.length === 1 ? ' match' : ' matches') : pad2(records.length) + ' on file';
        el.note.textContent = query ? 'Filtered' : pad2(records.length) + ' on file';
        if (!query) {
            setStat('ratings', pad2(records.length));
            setStat('in training', pad2(records.filter(function (e) { return e.qualification && e.qualification.ongoing; }).length));
        }
    }

    function load(query) {
        if (abort) abort.abort();
        abort = 'AbortController' in window ? new AbortController() : null;
        el.note.textContent = 'Scanning…';
        grid.setAttribute('aria-busy', 'true');

        fetch(cfg.list + '?institution=' + encodeURIComponent(query || ''), {
            headers: { 'Accept': 'application/json' },
            credentials: 'same-origin',
            signal: abort ? abort.signal : undefined
        }).then(function (res) {
            if (!res.ok) throw new Error('HTTP ' + res.status);
            return res.json();
        }).then(function (data) {
            records = Array.isArray(data) ? data : [];
            render(query);
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
            timer = setTimeout(function () { load(currentQuery()); }, 300);
        });
    }
    if (el.form) el.form.addEventListener('submit', function (e) { e.preventDefault(); clearTimeout(timer); load(currentQuery()); });
    if (el.retry) el.retry.addEventListener('click', function () { load(currentQuery()); });

    /* ---------- endorse (POST /api/v1/education/<id>/star/, a toggle) ---------- */
    function toggleStar(edu, btn) {
        if (btn.getAttribute('aria-busy') === 'true') return;  // no double toggles
        btn.setAttribute('aria-busy', 'true');
        api(url(cfg.star, edu.id), 'POST').then(function (data) {
            // the API answers with the whole record, so copy the fresh numbers over
            edu.is_starred = !!data.is_starred;
            edu.star_count = data.star_count || 0;
            btn.classList.toggle('is-on', edu.is_starred);
            btn.setAttribute('aria-pressed', String(edu.is_starred));
            btn.querySelector('.ab-commend-label').textContent = edu.is_starred ? 'Endorsed' : 'Endorse';
            btn.querySelector('.ab-commend-count').textContent = pad2(edu.star_count);
            AB.announce(edu.is_starred ? 'Endorsed ' + edu.institution : 'Endorsement withdrawn');
        }).catch(function (err) {
            failToast('Endorse', err);
        }).then(function () { btn.removeAttribute('aria-busy'); });
    }

    /* ---------- field errors (DRF 400: {field: ["message", …]}) ---------- */
    function clearErrors(form) {
        form.querySelectorAll('[data-ab-error-for]').forEach(function (p) { p.textContent = ''; p.hidden = true; });
        form.querySelectorAll('.ab-field.has-error').forEach(function (f) { f.classList.remove('has-error'); });
    }

    function showErrors(form, errors) {
        Object.keys(errors || {}).forEach(function (name) {
            var slot = form.querySelector('[data-ab-error-for="' + name + '"]');
            if (slot) {
                slot.textContent = [].concat(errors[name]).join(' ');
                slot.hidden = false;
                slot.closest('.ab-field').classList.add('has-error');
            }
        });
        var first = form.querySelector('.ab-field.has-error input, .ab-field.has-error select, .ab-field.has-error textarea');
        if (first) first.focus();
    }

    // The five model fields only (so the form's CSRF input isn't sent as data).
    // The edit form uses the "edit-" prefix, so its inputs are named edit-institution etc.
    function readFields(form) {
        var prefix = form.dataset.prefix || '';
        var payload = {};
        FIELDS.forEach(function (name) {
            var input = form.elements[prefix + name];
            if (input) payload[name] = input.value;
        });
        return payload;
    }

    function busy(button, on, label) {
        button.disabled = on;
        if (label) button.textContent = label;
    }

    /* ---------- add qualification (POST /api/v1/education/) ---------- */
    if (el.createForm && cfg.isSuperuser) {
        if (el.modal) el.modal.addEventListener('toggle', function (e) {
            if (e.newState === 'open') {
                var first = el.createForm.querySelector('input, select, textarea');
                if (first) setTimeout(function () { first.focus(); }, 30);
            } else { clearErrors(el.createForm); }
        });

        el.createForm.addEventListener('submit', function (e) {
            e.preventDefault();
            var submit = el.createForm.querySelector('button[type="submit"]');
            if (submit.disabled) return;
            busy(submit, true, 'Logging…');
            clearErrors(el.createForm);

            api(cfg.list, 'POST', readFields(el.createForm)).then(function (edu) {
                el.createForm.reset();
                if (el.modal && el.modal.hidePopover) el.modal.hidePopover();
                toast('Confirmed', edu.institution + ' added to the record.', 'success');
                if (el.input) el.input.value = '';
                load('');
            }).catch(function (err) {
                showErrors(el.createForm, err.fields);
                failToast('Logging', err);
            }).then(function () { busy(submit, false, 'Log rating'); });
        });
    }

    /* ---------- amend qualification (PATCH /api/v1/education/<id>/) ---------- */
    var editing = null;
    function openEdit(edu) {
        if (!el.editModal || !el.editForm) {  // no dialog on the page: use the Tugas 3 edit page
            window.location.href = url(cfg.edit, edu.id);
            return;
        }
        editing = edu;
        clearErrors(el.editForm);
        var prefix = el.editForm.dataset.prefix || '';
        FIELDS.forEach(function (name) {
            var input = el.editForm.elements[prefix + name];
            if (input) input.value = edu[name] === null || edu[name] === undefined ? '' : edu[name];
        });
        el.editForm.action = url(cfg.edit, edu.id);  // no-JS fallback target
        if (el.editCode) el.editCode.textContent = (edu.qualification && edu.qualification.code) || 'Amend rating';
        if (el.editModal.showPopover) el.editModal.showPopover();
        var first = el.editForm.querySelector('input, select, textarea');
        if (first) setTimeout(function () { first.focus(); }, 30);
    }

    if (el.editForm) {
        el.editForm.addEventListener('submit', function (e) {
            e.preventDefault();
            if (!editing) return;
            var edu = editing;
            var submit = el.editForm.querySelector('button[type="submit"]');
            if (submit.disabled) return;
            clearErrors(el.editForm);

            // PATCH carries only what changed; untouched fields stay as they are on the server
            var values = readFields(el.editForm);
            var changes = {};
            FIELDS.forEach(function (name) {
                var before = edu[name] === null || edu[name] === undefined ? '' : String(edu[name]);
                if (name in values && values[name] !== before) changes[name] = values[name];
            });
            if (!Object.keys(changes).length) {
                toast('No change', 'Nothing to amend on ' + edu.institution + '.', 'normal');
                return;
            }

            busy(submit, true, 'Saving…');
            api(url(cfg.detail, edu.id), 'PATCH', changes).then(function (updated) {
                if (el.editModal.hidePopover && el.editModal.matches(':popover-open')) el.editModal.hidePopover();
                toast('Confirmed', updated.institution + ' amended.', 'success');
                editing = null;
                load(currentQuery());
            }).catch(function (err) {
                showErrors(el.editForm, err.fields);
                failToast('Amendment', err);
            }).then(function () { busy(submit, false, 'Save amendment'); });
        });
    }

    /* ---------- scrub (DELETE /api/v1/education/<id>/) ---------- */
    var scrubbing = null;
    function openScrub(edu) {
        scrubbing = edu;
        el.scrubForm.action = url(cfg.del, edu.id);  // fallback if the fetch below never runs
        el.scrubName.textContent = edu.institution;
        if (el.scrub.showPopover) el.scrub.showPopover();
        else if (window.confirm('Scrub ' + edu.institution + '?')) scrub();
    }

    function scrub() {
        if (!scrubbing) return;
        var edu = scrubbing;
        var submit = el.scrubForm.querySelector('button[type="submit"]');
        if (submit) submit.disabled = true;
        api(url(cfg.detail, edu.id), 'DELETE').then(function () {
            if (el.scrub.hidePopover && el.scrub.matches(':popover-open')) el.scrub.hidePopover();
            toast('Confirmed', edu.institution + ' scrubbed from the record.', 'success');
            scrubbing = null;
            load(currentQuery());
        }).catch(function (err) {
            failToast('Scrub', err);
        }).then(function () { if (submit) submit.disabled = false; });
    }

    if (el.scrubForm) {
        el.scrubForm.addEventListener('submit', function (e) {
            e.preventDefault();
            scrub();
        });
    }

    load(currentQuery());
})();
