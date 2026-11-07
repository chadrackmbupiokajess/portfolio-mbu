/* =========================================================================
   Page projet : like du projet, agrandissement de l'image, commentaires
   (publication, réponses, j'aime, modification, suppression, signalement).
   Dépend de site.js (window.Site).
   ========================================================================= */
(function () {
    'use strict';

    function post(url, body) {
        return fetch(url, {
            method: 'POST',
            body: body || new FormData(),
            credentials: 'same-origin',
            headers: { 'X-CSRFToken': Site.csrfToken(), 'X-Requested-With': 'XMLHttpRequest' }
        }).then(function (r) {
            if (r.redirected && /login/.test(r.url)) { window.location.href = r.url; throw new Error('login'); }
            return r.json();
        });
    }

    function errorText(data) {
        if (!data) return 'Une erreur est survenue. Réessayez.';
        if (typeof data.error === 'string') return data.error;
        if (data.errors && typeof data.errors === 'object') {
            var first = Object.values(data.errors)[0];
            if (Array.isArray(first) && first.length) return first[0];
        }
        return 'Une erreur est survenue. Réessayez.';
    }

    function updateCount(delta) {
        var el = document.querySelector('[data-comment-count]');
        if (!el) return;
        var n = Math.max(0, (parseInt(el.getAttribute('data-comment-count'), 10) || 0) + delta);
        el.setAttribute('data-comment-count', n);
        el.textContent = n + ' commentaire' + (n > 1 ? 's' : '');
    }

    document.addEventListener('DOMContentLoaded', function () {

        /* ---------- J'aime le projet ---------- */
        var likeBtn = document.querySelector('[data-like-project]');
        if (likeBtn) {
            likeBtn.addEventListener('click', function () {
                if (likeBtn.hasAttribute('data-login-url')) {
                    window.location.href = likeBtn.getAttribute('data-login-url');
                    return;
                }
                likeBtn.disabled = true;
                post(likeBtn.getAttribute('data-like-project'))
                    .then(function (data) {
                        likeBtn.classList.toggle('is-liked', !!data.liked);
                        likeBtn.setAttribute('aria-pressed', data.liked ? 'true' : 'false');
                        likeBtn.querySelector('i').className = 'bi ' + (data.liked ? 'bi-heart-fill' : 'bi-heart');
                        likeBtn.querySelector('[data-like-count]').textContent = data.likes_count;
                    })
                    .catch(function (e) { if (e.message !== 'login') Site.toast('Action impossible pour le moment', 'error'); })
                    .finally(function () { likeBtn.disabled = false; });
            });
        }

        /* ---------- Agrandissement de l'image ---------- */
        var lightbox = document.getElementById('lightbox');
        var opener = document.querySelector('[data-lightbox-src]');
        if (lightbox && opener) {
            var img = lightbox.querySelector('img');
            var closeBtn = lightbox.querySelector('[data-close]');
            var open = function () {
                img.src = opener.getAttribute('data-lightbox-src');
                lightbox.classList.add('is-open');
                document.body.style.overflow = 'hidden';
                closeBtn.focus();
            };
            var close = function () {
                lightbox.classList.remove('is-open');
                document.body.style.overflow = '';
                opener.focus();
            };
            opener.addEventListener('click', open);
            closeBtn.addEventListener('click', close);
            lightbox.addEventListener('click', function (e) { if (e.target === lightbox) close(); });
            document.addEventListener('keydown', function (e) {
                if (e.key === 'Escape' && lightbox.classList.contains('is-open')) close();
            });
        }

        /* ---------- Publier un commentaire ---------- */
        var composer = document.getElementById('comment-form');
        var list = document.getElementById('comment-list');
        if (composer && list) {
            composer.addEventListener('submit', function (e) {
                e.preventDefault();
                var btn = composer.querySelector('[type=submit]');
                var textarea = composer.querySelector('textarea');
                if (!textarea.value.trim()) { textarea.focus(); return; }
                btn.disabled = true;
                post(composer.action, new FormData(composer))
                    .then(function (data) {
                        if (!data.success) { Site.toast(errorText(data), 'error'); return; }
                        var empty = document.getElementById('comments-empty');
                        if (empty) empty.remove();
                        list.insertAdjacentHTML('afterbegin', data.comment_html);
                        composer.reset();
                        updateCount(1);
                        Site.toast('Commentaire publié');
                    })
                    .catch(function (e) { if (e.message !== 'login') Site.toast('Connexion impossible. Réessayez.', 'error'); })
                    .finally(function () { btn.disabled = false; });
            });
        }

        /* ---------- Actions sur les commentaires (délégation) ---------- */
        document.addEventListener('click', function (e) {
            var btn = e.target.closest('[data-c-action]');
            if (!btn) return;
            var comment = btn.closest('.comment');
            var action = btn.getAttribute('data-c-action');
            var url = btn.getAttribute('data-url');

            if (action === 'login') {
                window.location.href = url;
                return;
            }

            if (action === 'like') {
                btn.disabled = true;
                post(url).then(function (data) {
                    if (!data.success) { Site.toast(errorText(data), 'error'); return; }
                    btn.classList.toggle('is-liked', data.liked);
                    btn.setAttribute('aria-pressed', data.liked ? 'true' : 'false');
                    btn.querySelector('i').className = 'bi ' + (data.liked ? 'bi-hand-thumbs-up-fill' : 'bi-hand-thumbs-up');
                    btn.querySelector('[data-count]').textContent = data.likes_count > 0 ? data.likes_count : '';
                }).catch(function (e) { if (e.message !== 'login') Site.toast('Action impossible pour le moment', 'error'); })
                  .finally(function () { btn.disabled = false; });
            }

            if (action === 'reply') {
                var box = comment.querySelector(':scope > div > .reply-box');
                if (!box) return;
                box.hidden = !box.hidden;
                btn.setAttribute('aria-expanded', box.hidden ? 'false' : 'true');
                if (!box.hidden) box.querySelector('textarea').focus();
            }

            if (action === 'cancel-reply') {
                var rb = btn.closest('.reply-box');
                rb.hidden = true;
                rb.querySelector('textarea').value = '';
            }

            if (action === 'share') {
                var link = window.location.href.split('#')[0] + '#' + comment.id;
                Site.copyText(link).then(function (ok) {
                    Site.toast(ok ? 'Lien du commentaire copié' : 'Impossible de copier le lien', ok ? 'success' : 'error');
                });
            }

            if (action === 'delete') {
                if (!window.confirm('Supprimer ce commentaire ? Cette action est définitive.')) return;
                post(url).then(function (data) {
                    if (!data.success) { Site.toast(errorText(data), 'error'); return; }
                    var isTop = !comment.parentElement.classList.contains('replies');
                    comment.remove();
                    if (isTop) updateCount(-1);
                    Site.toast('Commentaire supprimé');
                }).catch(function (e) { if (e.message !== 'login') Site.toast('Action impossible pour le moment', 'error'); });
            }

            if (action === 'report') {
                if (!window.confirm('Signaler ce commentaire comme inapproprié ?')) return;
                post(url).then(function (data) {
                    Site.toast(data.success ? 'Commentaire signalé. Merci.' : errorText(data), data.success ? 'success' : 'error');
                }).catch(function (e) { if (e.message !== 'login') Site.toast('Action impossible pour le moment', 'error'); });
            }

            if (action === 'edit') {
                var textEl = comment.querySelector(':scope > div > .c-text');
                if (!textEl || comment.querySelector(':scope > div > .edit-box')) return;
                var editBox = document.createElement('form');
                editBox.className = 'reply-box edit-box';
                editBox.innerHTML =
                    '<label class="visually-hidden" for="edit-' + comment.id + '">Modifier le commentaire</label>' +
                    '<textarea id="edit-' + comment.id + '" class="textarea-site" name="text" maxlength="5000" required></textarea>' +
                    '<div class="row-actions">' +
                    '<button type="button" class="btn-site btn-outline-site btn-sm-site" data-edit-cancel>Annuler</button>' +
                    '<button type="submit" class="btn-site btn-primary-site btn-sm-site">Enregistrer</button></div>';
                editBox.querySelector('textarea').value = textEl.textContent.trim();
                textEl.hidden = true;
                textEl.after(editBox);
                editBox.querySelector('textarea').focus();
                editBox.querySelector('[data-edit-cancel]').addEventListener('click', function () {
                    editBox.remove();
                    textEl.hidden = false;
                });
                editBox.addEventListener('submit', function (ev) {
                    ev.preventDefault();
                    var fd = new FormData(editBox);
                    post(url, fd).then(function (data) {
                        if (!data.success) { Site.toast(errorText(data), 'error'); return; }
                        textEl.textContent = data.new_text;
                        textEl.hidden = false;
                        editBox.remove();
                        var head = comment.querySelector(':scope > div > .c-head');
                        if (head && !head.querySelector('.edited')) {
                            var tag = document.createElement('span');
                            tag.className = 'edited';
                            tag.textContent = '(modifié)';
                            head.appendChild(tag);
                        }
                        Site.toast('Commentaire modifié');
                    }).catch(function (e) { if (e.message !== 'login') Site.toast('Action impossible pour le moment', 'error'); });
                });
            }
        });

        /* ---------- Publier une réponse ---------- */
        document.addEventListener('submit', function (e) {
            var form = e.target.closest('form[data-reply-form]');
            if (!form) return;
            e.preventDefault();
            var textarea = form.querySelector('textarea');
            if (!textarea.value.trim()) { textarea.focus(); return; }
            var btn = form.querySelector('[type=submit]');
            btn.disabled = true;
            post(form.action, new FormData(form))
                .then(function (data) {
                    if (!data.success) { Site.toast(errorText(data), 'error'); return; }
                    var parent = form.closest('.comment');
                    var replies = parent.querySelector(':scope > div > .replies');
                    if (!replies) {
                        replies = document.createElement('ul');
                        replies.className = 'replies';
                        form.before(replies);
                    }
                    replies.insertAdjacentHTML('beforeend', data.reply_html);
                    form.reset();
                    form.hidden = true;
                    Site.toast('Réponse publiée');
                })
                .catch(function (e) { if (e.message !== 'login') Site.toast('Connexion impossible. Réessayez.', 'error'); })
                .finally(function () { btn.disabled = false; });
        });

        /* ---------- Ctrl/Cmd + Entrée pour publier ---------- */
        document.addEventListener('keydown', function (e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && e.target.matches('.comments textarea')) {
                e.preventDefault();
                var f = e.target.form;
                if (f) f.requestSubmit();
            }
        });
    });
})();
