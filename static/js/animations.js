/**
 * Gestion des animations et effets visuels
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialiser AOS (Animate On Scroll)
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true,
            mirror: false
        });
    }
    
    // Animation au survol des cartes de projet
    const projectCards = document.querySelectorAll('.project-card, .card');
    projectCards.forEach(card => {
        card.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
        
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0,0,0,0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.05)';
        });
    });
    
    // Animation des compétences
    const skillBars = document.querySelectorAll('.skill-progress');
    
    const animateSkillBars = function() {
        skillBars.forEach(bar => {
            const width = bar.getAttribute('data-width') || '100%';
            bar.style.width = '0';
            
            // Réinitialiser pour déclencher l'animation
            void bar.offsetWidth;
            
            // Animer la barre de compétence
            bar.style.width = width;
            bar.style.transition = 'width 1.5s ease-in-out';
        });
    };
    
    // Observer l'intersection pour déclencher l'animation des compétences
    if ('IntersectionObserver' in window) {
        const skillObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateSkillBars();
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        skillBars.forEach(bar => {
            skillObserver.observe(bar);
        });
    } else {
        // Fallback pour les navigateurs qui ne supportent pas IntersectionObserver
        window.addEventListener('load', animateSkillBars);
    }
    
    // Animation de chargement des éléments au défilement
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.3;
            
            if (elementPosition < screenPosition) {
                element.classList.add('animated');
            }
        });
    };
    
    // Écouter l'événement de défilement
    window.addEventListener('scroll', animateOnScroll);
    
    // Démarrer l'animation au chargement de la page
    window.addEventListener('load', animateOnScroll);
    
    // Effet de parallaxe pour les éléments avec la classe 'parallax'
    const parallaxElements = document.querySelectorAll('.parallax');
    
    const updateParallax = function() {
        const scrollTop = window.pageYOffset;
        
        parallaxElements.forEach(element => {
            const speed = parseFloat(element.getAttribute('data-parallax-speed')) || 0.5;
            const yPos = -(scrollTop * speed);
            element.style.transform = `translate3d(0, ${yPos}px, 0)`;
        });
    };
    
    // Optimiser les performances avec requestAnimationFrame
    let ticking = false;
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(function() {
                updateParallax();
                ticking = false;
            });
            ticking = true;
        }
    });
    
    // Animation des compteurs numériques
    const counters = document.querySelectorAll('.counter');
    
    const startCounter = function(counter) {
        const target = +counter.getAttribute('data-target');
        const count = +counter.innerText;
        const duration = 2000; // 2 secondes
        const step = (target / duration) * 10;
        
        if (count < target) {
            counter.innerText = Math.ceil(count + step);
            setTimeout(() => startCounter(counter), 10);
        } else {
            counter.innerText = target;
        }
    };
    
    // Observer l'intersection pour déclencher les compteurs
    if ('IntersectionObserver' in window) {
        const counterObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    startCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        counters.forEach(counter => {
            counterObserver.observe(counter);
        });
    }
    
    // Animation des onglets
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabPanes.forEach(pane => {
        pane.addEventListener('show.bs.tab', function() {
            const activeTab = this.querySelector('.active');
            
            if (activeTab) {
                activeTab.classList.remove('fade');
                activeTab.classList.remove('show');
                activeTab.classList.remove('active');
            }
            
            const newTab = this.querySelector('.tab-pane');
            if (newTab) {
                newTab.classList.add('fade');
                newTab.classList.add('show');
                newTab.classList.add('active');
            }
        });
    });
    
    // Animation des modales
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            this.style.display = 'block';
            this.classList.add('show');
            
            // Ajouter une classe au body pour empêcher le défilement
            document.body.classList.add('modal-open');
            
            // Ajouter un fond sombre
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            document.body.appendChild(backdrop);
        });
        
        modal.addEventListener('hidden.bs.modal', function() {
            this.style.display = 'none';
            this.classList.remove('show');
            
            // Supprimer la classe du body
            document.body.classList.remove('modal-open');
            
            // Supprimer le fond sombre
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
        });
    });
});

// Exposer des fonctions pour une utilisation externe
const Animations = {
    /**
     * Anime un élément avec une classe CSS
     * @param {HTMLElement} element - L'élément à animer
     * @param {string} animationClass - La classe d'animation à ajouter
     * @param {Function} callback - Fonction de rappel après l'animation
     */
    animateElement: function(element, animationClass, callback) {
        if (!element) return;
        
        // Réinitialiser l'animation
        element.style.animation = 'none';
        void element.offsetWidth; // Forcer le recalcul
        
        // Ajouter la classe d'animation
        element.classList.add(animationClass);
        
        // Supprimer la classe après l'animation
        const handleAnimationEnd = function() {
            element.classList.remove(animationClass);
            element.removeEventListener('animationend', handleAnimationEnd);
            
            if (typeof callback === 'function') {
                callback();
            }
        };
        
        element.addEventListener('animationend', handleAnimationEnd);
    },
    
    /**
     * Anime un élément avec une séquence de classes CSS
     * @param {HTMLElement} element - L'élément à animer
     * @param {Array} animationClasses - Tableau d'objets {class: string, duration: number}
     * @param {Function} callback - Fonction de rappel après la séquence d'animations
     */
    animateSequence: function(element, animationClasses, callback) {
        if (!element || !animationClasses.length) return;
        
        let index = 0;
        
        const playNextAnimation = function() {
            if (index >= animationClasses.length) {
                if (typeof callback === 'function') {
                    callback();
                }
                return;
            }
            
            const {class: animationClass, duration} = animationClasses[index++];
            
            // Appliquer l'animation
            Animations.animateElement(element, animationClass, () => {
                // Passer à l'animation suivante après la durée spécifiée
                setTimeout(playNextAnimation, duration || 0);
            });
        };
        
        playNextAnimation();
    },
    
    /**
     * Anime un élément avec un effet de rebond
     * @param {HTMLElement} element - L'élément à animer
     * @param {number} intensity - Intensité du rebond (1-5)
     */
    bounce: function(element, intensity = 2) {
        if (!element) return;
        
        const scale = 1 + (intensity * 0.1);
        
        element.style.transition = 'transform 0.2s ease';
        element.style.transform = `scale(${scale})`;
        
        setTimeout(() => {
            element.style.transform = 'scale(1)';
            
            // Réinitialiser la transition après l'animation
            setTimeout(() => {
                element.style.transition = '';
            }, 200);
        }, 200);
    },
    
    /**
     * Fait pulser un élément
     * @param {HTMLElement} element - L'élément à animer
     * @param {number} count - Nombre de pulsations
     * @param {number} duration - Durée de chaque pulsation en ms
     */
    pulse: function(element, count = 3, duration = 300) {
        if (!element) return;
        
        let currentCount = 0;
        const scale = 1.1;
        
        const pulseOnce = function() {
            if (currentCount >= count) {
                element.style.transform = '';
                element.style.transition = '';
                return;
            }
            
            element.style.transition = `transform ${duration/2}ms ease-in-out`;
            element.style.transform = `scale(${scale})`;
            
            setTimeout(() => {
                element.style.transform = 'scale(1)';
                currentCount++;
                
                if (currentCount < count) {
                    setTimeout(pulseOnce, duration/2);
                } else {
                    setTimeout(() => {
                        element.style.transition = '';
                    }, duration/2);
                }
            }, duration);
        };
        
        pulseOnce();
    },
    
    /**
     * Fait apparaître un élément avec un effet de fondu
     * @param {HTMLElement} element - L'élément à animer
     * @param {number} duration - Durée de l'animation en ms
     * @param {Function} callback - Fonction de rappel après l'animation
     */
    fadeIn: function(element, duration = 400, callback) {
        if (!element) return;
        
        element.style.opacity = '0';
        element.style.display = 'block';
        element.style.transition = `opacity ${duration}ms ease`;
        
        // Forcer le recalcul pour déclencher la transition
        void element.offsetWidth;
        
        element.style.opacity = '1';
        
        if (typeof callback === 'function') {
            setTimeout(callback, duration);
        }
    },
    
    /**
     * Fait disparaître un élément avec un effet de fondu
     * @param {HTMLElement} element - L'élément à animer
     * @param {number} duration - Durée de l'animation en ms
     * @param {Function} callback - Fonction de rappel après l'animation
     */
    fadeOut: function(element, duration = 400, callback) {
        if (!element) return;
        
        element.style.opacity = '1';
        element.style.transition = `opacity ${duration}ms ease`;
        
        // Forcer le recalcul pour déclencher la transition
        void element.offsetWidth;
        
        element.style.opacity = '0';
        
        setTimeout(() => {
            element.style.display = 'none';
            element.style.transition = '';
            
            if (typeof callback === 'function') {
                callback();
            }
        }, duration);
    },
    
    /**
     * Anime le défilement vers un élément
     * @param {HTMLElement} element - L'élément cible
     * @param {number} offset - Décalage en pixels par rapport au haut de l'élément
     * @param {number} duration - Durée de l'animation en ms
     */
    scrollToElement: function(element, offset = 0, duration = 800) {
        if (!element) return;
        
        const start = window.pageYOffset;
        const target = element.getBoundingClientRect().top + window.pageYOffset - offset;
        const distance = target - start;
        let startTime = null;
        
        function animation(currentTime) {
            if (startTime === null) startTime = currentTime;
            const timeElapsed = currentTime - startTime;
            const run = easeInOutQuad(timeElapsed, start, distance, duration);
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
};

// Exposer pour une utilisation globale
window.Animations = Animations;
