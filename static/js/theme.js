/**
 * Gestion du thème clair/sombre
 */

document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Vérifier le thème stocké ou utiliser les préférences du système
    const currentTheme = localStorage.getItem('theme') || 
                        (prefersDarkScheme.matches ? 'dark' : 'light');
    
    // Appliquer le thème actuel
    if (currentTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (themeToggle) {
            themeToggle.checked = true;
            themeToggle.innerHTML = '<i class="bi bi-sun"></i>';
        }
    }
    
    // Gérer le changement de thème
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // Appliquer le nouveau thème
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Mettre à jour l'icône
            if (newTheme === 'dark') {
                themeToggle.innerHTML = '<i class="bi bi-sun"></i>';
            } else {
                themeToggle.innerHTML = '<i class="bi bi-moon"></i>';
            }
            
            // Déclencher un événement personnalisé pour les composants qui en ont besoin
            document.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: newTheme } }));
        });
    }
    
    // Écouter les changements de préférences système
    prefersDarkScheme.addListener((e) => {
        if (!localStorage.getItem('theme')) {
            const newTheme = e.matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            document.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: newTheme } }));
        }
    });
});

/**
 * Fonction utilitaire pour forcer le reflow d'un élément
 * Utile pour les animations CSS
 */
function forceReflow(element) {
    return element.offsetHeight;
}
