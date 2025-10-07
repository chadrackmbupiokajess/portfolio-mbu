/**
 * Utilitaires JavaScript pour l'application
 */

/**
 * Affiche une notification à l'utilisateur
 * @param {string} message - Le message à afficher
 * @param {string} type - Le type de notification (success, error, warning, info)
 * @param {number} duration - Durée d'affichage en millisecondes (par défaut: 5000ms)
 */
function showNotification(message, type = 'info', duration = 5000) {
    // Créer l'élément de notification
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '1100';
    notification.style.maxWidth = '350px';
    notification.role = 'alert';
    
    // Contenu de la notification
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fermer"></button>
    `;
    
    // Ajouter la notification au corps du document
    document.body.appendChild(notification);
    
    // Supprimer la notification après la durée spécifiée
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 150);
    }, duration);
}

/**
 * Récupère un cookie par son nom
 * @param {string} name - Le nom du cookie à récupérer
 * @returns {string|null} - La valeur du cookie ou null s'il n'existe pas
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Vérifier si ce cookie correspond au nom recherché
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Formate une date au format lisible
 * @param {string|Date} date - La date à formater
 * @param {string} locale - La locale à utiliser (par défaut: 'fr-FR')
 * @returns {string} La date formatée
 */
function formatDate(date, locale = 'fr-FR') {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return dateObj.toLocaleDateString(locale, options);
}

/**
 * Met en forme un nombre avec des séparateurs de milliers
 * @param {number} number - Le nombre à formater
 * @param {string} locale - La locale à utiliser (par défaut: 'fr-FR')
 * @returns {string} Le nombre formaté
 */
function formatNumber(number, locale = 'fr-FR') {
    return new Intl.NumberFormat(locale).format(number);
}

/**
 * Met en majuscule la première lettre d'une chaîne
 * @param {string} string - La chaîne à formater
 * @returns {string} La chaîne avec la première lettre en majuscule
 */
function capitalizeFirstLetter(string) {
    if (!string) return '';
    return string.charAt(0).toUpperCase() + string.slice(1);
}

/**
 * Tronque une chaîne à une longueur maximale
 * @param {string} string - La chaîne à tronquer
 * @param {number} maxLength - La longueur maximale
 * @param {string} ellipsis - Le caractère d'ellipse (par défaut: '...')
 * @returns {string} La chaîne tronquée
 */
function truncate(string, maxLength, ellipsis = '...') {
    if (!string) return '';
    if (string.length <= maxLength) return string;
    return string.substring(0, maxLength) + ellipsis;
}

/**
 * Vérifie si un élément est visible dans la fenêtre
 * @param {HTMLElement} element - L'élément à vérifier
 * @returns {boolean} Vrai si l'élément est visible, faux sinon
 */
function isElementInViewport(element) {
    if (!element) return false;
    
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Fait défiler la page vers un élément en douceur
 * @param {string|HTMLElement} target - L'élément ou le sélecteur CSS de l'élément vers lequel faire défiler
 * @param {number} offset - Décalage en pixels par rapport au haut de l'élément (par défaut: 0)
 * @param {number} duration - Durée de l'animation en millisecondes (par défaut: 800ms)
 */
function smoothScrollTo(target, offset = 0, duration = 800) {
    let targetElement;
    
    if (typeof target === 'string') {
        targetElement = document.querySelector(target);
    } else if (target instanceof HTMLElement) {
        targetElement = target;
    } else {
        console.error('La cible doit être un sélecteur CSS ou un élément HTML');
        return;
    }
    
    if (!targetElement) {
        console.error('Élément non trouvé');
        return;
    }
    
    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - offset;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;
    
    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const run = easeInOutQuad(timeElapsed, startPosition, distance, duration);
        window.scrollTo(0, run);
        if (timeElapsed < duration) requestAnimationFrame(animation);
    }
    
    // Fonction d'accélération/décélération
    function easeInOutQuad(t, b, c, d) {
        t /= d/2;
        if (t < 1) return c/2*t*t + b;
        t--;
        return -c/2 * (t*(t-2) - 1) + b;
    }
    
    requestAnimationFrame(animation);
}

/**
 * Détecte si l'appareil est un appareil mobile
 * @returns {boolean} Vrai si c'est un appareil mobile, faux sinon
 */
function isMobileDevice() {
    return (typeof window.orientation !== "undefined") || (navigator.userAgent.indexOf('IEMobile') !== -1);
}

/**
 * Ajoute un écouteur d'événement avec délégation d'événements
 * @param {string} parentSelector - Le sélecteur du parent sur lequel écouter
 * @param {string} event - Le type d'événement à écouter
 * @param {string} childSelector - Le sélecteur de l'enfant qui déclenche l'événement
 * @param {Function} handler - La fonction de rappel à exécuter
 */
function delegateEvent(parentSelector, event, childSelector, handler) {
    const parent = document.querySelector(parentSelector);
    if (!parent) return;
    
    parent.addEventListener(event, function(e) {
        let target = e.target;
        
        // Vérifier si l'élément cible correspond au sélecteur enfant
        while (target && target !== this) {
            if (target.matches(childSelector)) {
                handler.call(target, e);
                break;
            }
            target = target.parentNode;
        }
    });
}

// Exporter les fonctions pour une utilisation dans d'autres fichiers
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = {
        showNotification,
        getCookie,
        formatDate,
        formatNumber,
        capitalizeFirstLetter,
        truncate,
        isElementInViewport,
        smoothScrollTo,
        isMobileDevice,
        delegateEvent
    };
}
