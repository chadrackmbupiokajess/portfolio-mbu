/* =========================================================================
   Scripts communs à toutes les pages
   - thème clair / sombre
   - menu mobile
   - bouton « retour en haut »
   - toasts (Site.toast)
   - compteur de notifications
   ========================================================================= */
(function () {
    'use strict';

    var root = document.documentElement;

    /* ---------- Utilitaires exposés ---------- */
    function getCookie(name) {
        var match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
        return match ? decodeURIComponent(match[1]) : null;
    }

    function csrfToken() {
        var input = document.querySelector('[name=csrfmiddlewaretoken]');
        return (input && input.value) || getCookie('csrftoken') || '';
    }

    function toast(message, type) {
        var zone = document.querySelector('.toast-zone');
        if (!zone) {
            zone = document.createElement('div');
            zone.className = 'toast-zone';
            zone.setAttribute('role', 'status');
            zone.setAttribute('aria-live', 'polite');
            document.body.appendChild(zone);
        }
        var el = document.createElement('div');
        el.className = 'toast-site' + (type === 'error' ? ' error' : '');
        var icon = document.createElement('i');
        icon.className = 'bi ' + (type === 'error' ? 'bi-exclamation-circle' : 'bi-check-circle');
        var text = document.createElement('span');
        text.textContent = message;
        el.appendChild(icon);
        el.appendChild(text);
        zone.appendChild(el);
        setTimeout(function () { el.remove(); }, 4000);
    }

    async function copyText(text) {
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(text);
                return true;
            }
        } catch (e) { /* on tente la méthode de secours */ }
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        var ok = false;
        try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
        ta.remove();
        return ok;
    }

    window.Site = { getCookie: getCookie, csrfToken: csrfToken, toast: toast, copyText: copyText };

    document.addEventListener('DOMContentLoaded', function () {

        /* ---------- Thème ---------- */
        var themeBtn = document.getElementById('theme-toggle');
        function syncThemeIcon() {
            if (!themeBtn) return;
            var dark = root.getAttribute('data-theme') === 'dark';
            themeBtn.querySelector('i').className = dark ? 'bi bi-sun' : 'bi bi-moon';
            themeBtn.setAttribute('aria-label', dark ? 'Passer au thème clair' : 'Passer au thème sombre');
        }
        syncThemeIcon();
        if (themeBtn) {
            themeBtn.addEventListener('click', function () {
                var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
                root.setAttribute('data-theme', next);
                try { localStorage.setItem('theme', next); } catch (e) { /* stockage indisponible */ }
                syncThemeIcon();
            });
        }

        /* ---------- Menu mobile ---------- */
        var navToggle = document.querySelector('.nav-toggle');
        var navMain = document.getElementById('nav-main');
        if (navToggle && navMain) {
            navToggle.addEventListener('click', function () {
                var open = navMain.classList.toggle('is-open');
                navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
                navToggle.querySelector('i').className = open ? 'bi bi-x-lg' : 'bi bi-list';
            });
            document.addEventListener('keydown', function (e) {
                if (e.key === 'Escape' && navMain.classList.contains('is-open')) {
                    navToggle.click();
                    navToggle.focus();
                }
            });
        }

        /* ---------- Retour en haut ---------- */
        var toTop = document.querySelector('.to-top');
        if (toTop) {
            window.addEventListener('scroll', function () {
                toTop.classList.toggle('is-visible', window.scrollY > 600);
            }, { passive: true });
            toTop.addEventListener('click', function () { window.scrollTo({ top: 0 }); });
        }

        /* ---------- Barre flottante mobile ----------
           Toujours fixe en bas ; elle s'efface seulement pendant la saisie
           (clavier ouvert) pour ne pas cacher le champ. */
        var bottomNav = document.querySelector('.bottom-nav');
        if (bottomNav) {
            document.addEventListener('focusin', function (e) {
                if (e.target.matches('input, textarea, select, [contenteditable]')) {
                    bottomNav.classList.add('is-hidden');
                }
            });
            document.addEventListener('focusout', function () {
                bottomNav.classList.remove('is-hidden');
            });
        }

        /* ---------- Messages Django (fermeture) ---------- */
        document.querySelectorAll('.flash button').forEach(function (btn) {
            btn.addEventListener('click', function () { btn.closest('.flash').remove(); });
        });

        /* ---------- Afficher / masquer un mot de passe ---------- */
        document.querySelectorAll('[data-toggle-password]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var input = btn.parentElement.querySelector('input');
                var show = input.type === 'password';
                input.type = show ? 'text' : 'password';
                btn.querySelector('i').className = show ? 'bi bi-eye-slash' : 'bi bi-eye';
                btn.setAttribute('aria-label', show ? 'Masquer le mot de passe' : 'Afficher le mot de passe');
            });
        });

        /* ---------- Copier le lien de la page ---------- */
        document.querySelectorAll('[data-copy-link]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                copyText(window.location.href.split('#')[0]).then(function (ok) {
                    toast(ok ? 'Lien copié' : 'Impossible de copier le lien', ok ? 'success' : 'error');
                });
            });
        });

        /* ---------- Notifications non lues ---------- */
        var bell = document.querySelector('[data-notif-url]');
        if (bell) {
            var refresh = function () {
                fetch(bell.getAttribute('data-notif-url'), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                    .then(function (r) { return r.ok ? r.json() : null; })
                    .then(function (data) {
                        if (!data) return;
                        var badge = bell.querySelector('.badge-dot');
                        if (data.unread_count > 0) {
                            if (!badge) {
                                badge = document.createElement('span');
                                badge.className = 'badge-dot';
                                bell.appendChild(badge);
                            }
                            badge.textContent = data.unread_count > 99 ? '99+' : data.unread_count;
                        } else if (badge) {
                            badge.remove();
                        }
                    })
                    .catch(function () { /* silencieux : non bloquant */ });
            };
            setInterval(refresh, 60000);
        }
    });
})();
