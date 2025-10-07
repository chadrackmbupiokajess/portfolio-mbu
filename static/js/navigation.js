/**
 * Gestion de la navigation et des interactions de la barre de navigation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Éléments du DOM
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    const navLinks = document.querySelectorAll('.nav-link');
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    const backToTopBtn = document.getElementById('back-to-top');
    
    // Activer les tooltips Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Gérer le clic sur le bouton du menu mobile
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
            
            // Animer l'icône du bouton hamburger
            this.classList.toggle('collapsed');
            this.setAttribute('aria-expanded', this.classList.contains('collapsed') ? 'false' : 'true');
            
            // Ajouter/supprimer la classe 'navbar-expanded' sur le body
            document.body.classList.toggle('navbar-expanded', !this.classList.contains('collapsed'));
        });
    }
    
    // Fermer le menu mobile lors du clic sur un lien de navigation
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (navbarCollapse.classList.contains('show')) {
                navbarCollapse.classList.remove('show');
                navbarToggler.classList.add('collapsed');
                navbarToggler.setAttribute('aria-expanded', 'false');
                document.body.classList.remove('navbar-expanded');
            }
        });
    });
    
    // Gérer les menus déroulants au survol sur les écrans larges
    if (window.innerWidth >= 992) {
        dropdownToggles.forEach(toggle => {
            toggle.addEventListener('mouseenter', function() {
                const dropdownMenu = this.nextElementSibling;
                if (dropdownMenu && dropdownMenu.classList.contains('dropdown-menu')) {
                    this.setAttribute('aria-expanded', 'true');
                    dropdownMenu.classList.add('show');
                }
            });
            
            toggle.parentElement.addEventListener('mouseleave', function() {
                const dropdownMenu = this.querySelector('.dropdown-menu');
                if (dropdownMenu) {
                    this.querySelector('.dropdown-toggle').setAttribute('aria-expanded', 'false');
                    dropdownMenu.classList.remove('show');
                }
            });
        });
    }
    
    // Gérer le défilement fluide pour les ancres internes
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        // Ignorer les ancres vides ou les liens avec des classes spécifiques
        if (anchor.getAttribute('href') !== '#' && 
            !anchor.classList.contains('no-smooth-scroll') && 
            !anchor.hasAttribute('data-bs-toggle') &&
            !anchor.hasAttribute('role') &&
            !anchor.getAttribute('href').startsWith('#tab-')) {
                
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    // Calculer la position de défilement en tenant compte de la hauteur de la barre de navigation
                    const navbarHeight = document.querySelector('.navbar').offsetHeight;
                    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - navbarHeight - 20;
                    
                    // Effectuer le défilement fluide
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                    
                    // Mettre à jour l'URL sans recharger la page
                    if (history.pushState) {
                        history.pushState(null, null, targetId);
                    } else {
                        window.location.hash = targetId;
                    }
                }
            });
        }
    });
    
    // Afficher/masquer le bouton "Retour en haut"
    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopBtn.classList.add('show');
            } else {
                backToTopBtn.classList.remove('show');
            }
        });
        
        // Gérer le clic sur le bouton "Retour en haut"
        backToTopBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Gérer le rafraîchissement de la page avec une ancre dans l'URL
    window.addEventListener('load', function() {
        if (window.location.hash) {
            const targetId = window.location.hash;
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                // Délai pour s'assurer que tout est chargé
                setTimeout(() => {
                    const navbarHeight = document.querySelector('.navbar').offsetHeight;
                    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - navbarHeight - 20;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }, 100);
            }
        }
    });
    
    // Gérer les onglets avec attribut data-bs-toggle="tab"
    const tabLinks = document.querySelectorAll('a[data-bs-toggle="tab"]');
    tabLinks.forEach(tabLink => {
        tabLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetTab = document.querySelector(this.getAttribute('href'));
            const tabPane = targetTab.closest('.tab-pane');
            
            // Activer l'onglet parent si nécessaire
            if (tabPane && tabPane.id) {
                const parentTabLink = document.querySelector(`[data-bs-target="#${tabPane.id}"]`);
                if (parentTabLink) {
                    new bootstrap.Tab(parentTabLink).show();
                }
            }
            
            // Activer l'onglet actuel
            new bootstrap.Tab(this).show();
            
            // Défiler vers l'onglet si nécessaire
            if (window.innerWidth < 992) {
                this.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
            }
        });
    });
    
    // Gérer les popovers Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl, {
            trigger: 'focus', // Afficher le popover au clic
            html: true // Permettre le HTML dans le contenu du popover
        });
    });
    
    // Fermer les popovers lors du clic à l'extérieur
    document.addEventListener('click', function(e) {
        if (e.target.closest('[data-bs-toggle="popover"]') === null) {
            const popovers = document.querySelectorAll('.popover');
            popovers.forEach(popover => {
                const popoverInstance = bootstrap.Popover.getInstance(popover);
                if (popoverInstance) {
                    popoverInstance.hide();
                }
            });
        }
    });
});

// Exposer des fonctions pour une utilisation externe
const Navigation = {
    /**
     * Fait défiler la page vers un élément spécifique
     * @param {string} selector - Le sélecteur CSS de l'élément cible
     * @param {number} offset - Le décalage en pixels par rapport au haut de la page
     */
    scrollToElement: function(selector, offset = 0) {
        const element = document.querySelector(selector);
        if (element) {
            const navbarHeight = document.querySelector('.navbar').offsetHeight;
            const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
            const offsetPosition = elementPosition - navbarHeight - (offset || 0);
            
            window.scrollTo({
                top: offsetPosition,
                behavior: 's'
            });
        }
    },
    
    /**
     * Ouvre un onglet spécifique par son ID
     * @param {string} tabId - L'ID de l'onglet à ouvrir
     */
    openTab: function(tabId) {
        const tabLink = document.querySelector(`[data-bs-target="#${tabId}"]`);
        if (tabLink) {
            new bootstrap.Tab(tabLink).show();
        }
    },
    
    /**
     * Met à jour la classe active sur les liens de navigation
     * @param {string} sectionId - L'ID de la section active
     */
    updateActiveNavLink: function(sectionId) {
        // Supprimer la classe active de tous les liens
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            link.setAttribute('aria-current', null);
        });
        
        // Ajouter la classe active au lien correspondant
        const activeLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
            activeLink.setAttribute('aria-current', 'page');
        }
    }
};

// Exposer pour une utilisation globale
window.Navigation = Navigation;
