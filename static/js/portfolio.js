// Portfolio JavaScript - Fonctionnalités avancées

// Initialisation AOS (Animate On Scroll)
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser AOS si disponible
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true,
            offset: 100
        });
    }
    
    // Initialiser les fonctionnalités
    initializeCarousel();
    initializeLikeButtons();
    initializeSearchFilters();
    initializeNotifications();
    initializeScrollEffects();
});

// Gestion du carousel de projets
function initializeCarousel() {
    const carousel = document.getElementById('projectsCarousel');
    if (!carousel) return;
    
    let currentSlide = 0;
    const slides = carousel.querySelectorAll('.project-slide');
    const indicators = carousel.querySelectorAll('.indicator');
    const totalSlides = slides.length;
    
    if (totalSlides === 0) return;
    
    function updateCarousel() {
        slides.forEach((slide, index) => {
            slide.classList.toggle('active', index === currentSlide);
        });
        
        indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === currentSlide);
        });
    }
    
    function moveSlide(direction) {
        currentSlide += direction;
        
        if (currentSlide >= totalSlides) {
            currentSlide = 0;
        } else if (currentSlide < 0) {
            currentSlide = totalSlides - 1;
        }
        
        updateCarousel();
    }
    
    function goToSlide(slideIndex) {
        currentSlide = slideIndex;
        updateCarousel();
    }
    
    // Exposer les fonctions globalement
    window.moveSlide = moveSlide;
    window.goToSlide = goToSlide;
    
    // Auto-play
    let autoPlayInterval = setInterval(() => {
        moveSlide(1);
    }, 5000);
    
    // Pause auto-play au survol
    carousel.addEventListener('mouseenter', () => {
        clearInterval(autoPlayInterval);
    });
    
    carousel.addEventListener('mouseleave', () => {
        autoPlayInterval = setInterval(() => {
            moveSlide(1);
        }, 5000);
    });
    
    // Initialiser
    updateCarousel();
}

// Gestion des boutons like
function initializeLikeButtons() {
    document.addEventListener('click', function(e) {
        if (e.target.closest('.like-btn')) {
            e.preventDefault();
            const btn = e.target.closest('.like-btn');
            const projectId = btn.dataset.projectId;
            
            if (!projectId) return;
            
            fetch(`/project/${projectId}/like/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.liked) {
                    btn.classList.add('liked');
                    btn.innerHTML = '<i class="fas fa-heart"></i>';
                } else {
                    btn.classList.remove('liked');
                    btn.innerHTML = '<i class="far fa-heart"></i>';
                }
                
                const countElement = btn.querySelector('.like-count');
                if (countElement) {
                    countElement.textContent = data.likes_count;
                }
            })
            .catch(error => {
                console.error('Erreur lors du like:', error);
            });
        }
    });
}

// Gestion des filtres de recherche
function initializeSearchFilters() {
    const searchForm = document.getElementById('search-form');
    if (!searchForm) return;
    
    const searchInput = searchForm.querySelector('#search-input');
    const categorySelect = searchForm.querySelector('#category-select');
    const tagSelect = searchForm.querySelector('#tag-select');
    const statusSelect = searchForm.querySelector('#status-select');
    
    // Recherche en temps réel
    let searchTimeout;
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch();
            }, 500);
        });
    }
    
    // Filtres instantanés
    [categorySelect, tagSelect, statusSelect].forEach(select => {
        if (select) {
            select.addEventListener('change', performSearch);
        }
    });
    
    function performSearch() {
        const formData = new FormData(searchForm);
        const params = new URLSearchParams(formData);
        
        fetch(`/search/?${params.toString()}`)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newResults = doc.querySelector('#search-results');
                const currentResults = document.querySelector('#search-results');
                
                if (newResults && currentResults) {
                    currentResults.innerHTML = newResults.innerHTML;
                    
                    // Réinitialiser AOS pour les nouveaux éléments
                    if (typeof AOS !== 'undefined') {
                        AOS.refresh();
                    }
                }
            })
            .catch(error => {
                console.error('Erreur lors de la recherche:', error);
            });
    }
}

// Gestion des notifications
function initializeNotifications() {
    // Marquer les notifications comme lues au clic
    document.addEventListener('click', function(e) {
        if (e.target.closest('.notification-item')) {
            const notificationItem = e.target.closest('.notification-item');
            const notificationId = notificationItem.dataset.notificationId;
            
            if (notificationId && !notificationItem.classList.contains('read')) {
                fetch(`/notification/mark-as-read/${notificationId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                })
                .then(() => {
                    notificationItem.classList.add('read');
                    updateNotificationBadge();
                });
            }
        }
    });
    
    // Mettre à jour le badge de notifications
    function updateNotificationBadge() {
        fetch('/unread-notifications/')
            .then(response => response.json())
            .then(data => {
                const badge = document.getElementById('notification-badge');
                if (badge) {
                    if (data.unread_count > 0) {
                        badge.textContent = data.unread_count;
                        badge.style.display = 'inline-block';
                    } else {
                        badge.style.display = 'none';
                    }
                }
            });
    }
    
    // Vérifier les notifications toutes les 30 secondes
    setInterval(updateNotificationBadge, 30000);
}

// Effets de scroll
function initializeScrollEffects() {
    // Smooth scroll pour les ancres
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Parallax effect pour le hero
    const hero = document.querySelector('.hero-section');
    if (hero) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            hero.style.transform = `translateY(${rate}px)`;
        });
    }
    
    // Navbar background au scroll
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }
}

// Utilitaires
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Gestion des formulaires AJAX
function submitFormAjax(form, successCallback) {
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (successCallback) {
                successCallback(data);
            }
        } else {
            console.error('Erreur:', data.errors);
        }
    })
    .catch(error => {
        console.error('Erreur AJAX:', error);
    });
}

// Animations personnalisées
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);
    
    function updateCounter() {
        start += increment;
        if (start < target) {
            element.textContent = Math.floor(start);
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target;
        }
    }
    
    updateCounter();
}

// Initialiser les compteurs animés
function initializeCounters() {
    const counters = document.querySelectorAll('.stat-number');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.textContent);
                entry.target.textContent = '0';
                animateCounter(entry.target, target);
                observer.unobserve(entry.target);
            }
        });
    });
    
    counters.forEach(counter => {
        observer.observe(counter);
    });
}

// Initialiser au chargement
document.addEventListener('DOMContentLoaded', initializeCounters);