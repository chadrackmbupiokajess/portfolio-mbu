/**
 * Gestion centralisée des appels API
 */

class ApiClient {
    constructor() {
        this.baseUrl = '/api';
        this.csrfToken = this.getCsrfToken();
    }

    /**
     * Récupère le token CSRF depuis les cookies
     * @returns {string} Le token CSRF
     */
    getCsrfToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === ('csrftoken=')) {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Effectue une requête HTTP
     * @param {string} method - La méthode HTTP (GET, POST, PUT, DELETE, etc.)
     * @param {string} endpoint - L'endpoint de l'API (sans le préfixe /api)
     * @param {Object} [data=null] - Les données à envoyer (pour POST, PUT, PATCH)
     * @param {Object} [headers={}] - Les en-têtes HTTP supplémentaires
     * @returns {Promise<Object>} La réponse de l'API parsée en JSON
     */
    async request(method, endpoint, data = null, headers = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        // Configuration de la requête
        const config = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                ...headers
            },
            credentials: 'same-origin'
        };

        // Ajouter le token CSRF pour les méthodes non-GET
        if (this.csrfToken && method !== 'GET') {
            config.headers['X-CSRFToken'] = this.csrfToken;
        }

        // Ajouter les données pour les méthodes POST, PUT, PATCH
        if (data && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, config);
            
            // Vérifier si la réponse est au format JSON
            const contentType = response.headers.get('content-type');
            const isJson = contentType && contentType.includes('application/json');
            
            let responseData;
            
            if (isJson) {
                responseData = await response.json();
            } else {
                responseData = await response.text();
            }

            if (!response.ok) {
                // Gérer les erreurs HTTP
                const error = new Error(response.statusText);
                error.status = response.status;
                error.response = responseData;
                throw error;
            }

            return responseData;
            
        } catch (error) {
            console.error('API Request Error:', error);
            
            // Afficher une notification d'erreur à l'utilisateur
            if (typeof showNotification === 'function') {
                const errorMessage = error.response?.message || 'Une erreur est survenue lors de la communication avec le serveur.';
                showNotification(errorMessage, 'error');
            }
            
            throw error;
        }
    }

    // Méthodes HTTP simplifiées
    
    /**
     * Effectue une requête GET
     * @param {string} endpoint - L'endpoint de l'API
     * @param {Object} [headers={}] - Les en-têtes HTTP supplémentaires
     * @returns {Promise<Object>} La réponse de l'API
     */
    get(endpoint, headers = {}) {
        return this.request('GET', endpoint, null, headers);
    }

    /**
     * Effectue une requête POST
     * @param {string} endpoint - L'endpoint de l'API
     * @param {Object} data - Les données à envoyer
     * @param {Object} [headers={}] - Les en-têtes HTTP supplémentaires
     * @returns {Promise<Object>} La réponse de l'API
     */
    post(endpoint, data, headers = {}) {
        return this.request('POST', endpoint, data, headers);
    }

    /**
     * Effectue une requête PUT
     * @param {string} endpoint - L'endpoint de l'API
     * @param {Object} data - Les données à envoyer
     * @param {Object} [headers={}] - Les en-têtes HTTP supplémentaires
     * @returns {Promise<Object>} La réponse de l'API
     */
    put(endpoint, data, headers = {}) {
        return this.request('PUT', endpoint, data, headers);
    }

    /**
     * Effectue une requête PATCH
     * @param {string} endpoint - L'endpoint de l'API
     * @param {Object} data - Les données à envoyer
     * @param {Object} [headers={}] - Les en-têtes HTTP supplémentaires
     * @returns {Promise<Object>} La réponse de l'API
     */
    patch(endpoint, data, headers = {}) {
        return this.request('PATCH', endpoint, data, headers);
    }

    /**
     * Effectue une requête DELETE
     * @param {string} endpoint - L'endpoint de l'API
     * @param {Object} [data=null] - Les données à envoyer
     * @param {Object} [headers={}] - Les en-têtes HTTP supplémentaires
     * @returns {Promise<Object>} La réponse de l'API
     */
    delete(endpoint, data = null, headers = {}) {
        return this.request('DELETE', endpoint, data, headers);
    }

    /**
     * Télécharge un fichier
     * @param {string} endpoint - L'endpoint de l'API
     * @param {Object} data - Les données du formulaire
     * @param {string} fileInputName - Le nom du champ de fichier
     * @param {Object} [headers={}] - Les en-têtes HTTP supplémentaires
     * @returns {Promise<Object>} La réponse de l'API
     */
    async uploadFile(endpoint, data, fileInputName, headers = {}) {
        const formData = new FormData();
        
        // Ajouter les champs de données
        Object.keys(data).forEach(key => {
            formData.append(key, data[key]);
        });
        
        // Ajouter le fichier s'il est spécifié
        const fileInput = document.querySelector(`input[name="${fileInputName}"]`);
        if (fileInput && fileInput.files.length > 0) {
            formData.append(fileInputName, fileInput.files[0]);
        }
        
        // Configuration de la requête
        const config = {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                ...headers
            },
            body: formData,
            credentials: 'same-origin'
        };
        
        // Ajouter le token CSRF
        if (this.csrfToken) {
            config.headers['X-CSRFToken'] = this.csrfToken;
        }
        
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, config);
            const responseData = await response.json();
            
            if (!response.ok) {
                const error = new Error(response.statusText);
                error.status = response.status;
                error.response = responseData;
                throw error;
            }
            
            return responseData;
            
        } catch (error) {
            console.error('File Upload Error:', error);
            
            // Afficher une notification d'erreur à l'utilisateur
            if (typeof showNotification === 'function') {
                const errorMessage = error.response?.message || 'Une erreur est survenue lors du téléchargement du fichier.';
                showNotification(errorMessage, 'error');
            }
            
            throw error;
        }
    }
}

// Créer une instance unique de l'API client
const api = new ApiClient();

// Exporter pour une utilisation dans d'autres fichiers
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = api;
}
