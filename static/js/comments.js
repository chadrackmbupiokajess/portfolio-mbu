/**
 * Gestion des interactions des commentaires (commentaires et réponses)
 */

// Fonction utilitaire pour afficher une notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.notifications-container');
    if (!container) {
        // Créer un conteneur s'il n'existe pas
        const newContainer = document.createElement('div');
        newContainer.className = 'notifications-container position-fixed';
        newContainer.style.top = '20px';
        newContainer.style.right = '20px';
        newContainer.style.zIndex = '1100';
        newContainer.style.maxWidth = '350px';
        document.body.appendChild(newContainer);
        newContainer.appendChild(notification);
    } else {
        container.appendChild(notification);
    }
    
    // Supprimer la notification après 5 secondes
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 150);
    }, 5000);
}

// Gestion des likes de commentaires
document.addEventListener('click', function(e) {
    // Gestion des likes
    if (e.target.closest('.like-comment-btn')) {
        e.preventDefault();
        const button = e.target.closest('.like-comment-btn');
        const commentId = button.dataset.commentId;
        
        // Mettre à jour l'interface utilisateur immédiatement pour un retour visuel rapide
        const likeCount = button.querySelector('.like-count');
        const isLiked = button.classList.contains('liked');
        
        if (isLiked) {
            button.classList.remove('liked');
            button.querySelector('i').classList.replace('fas', 'far');
            likeCount.textContent = parseInt(likeCount.textContent) - 1;
        } else {
            button.classList.add('liked');
            button.querySelector('i').classList.replace('far', 'fas');
            likeCount.textContent = parseInt(likeCount.textContent) + 1;
        }
        
        // Envoyer la requête AJAX
        fetch(`/comment/${commentId}/like/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                // Annuler les changements visuels en cas d'erreur
                if (isLiked) {
                    button.classList.add('liked');
                    button.querySelector('i').classList.replace('far', 'fas');
                    likeCount.textContent = parseInt(likeCount.textContent) + 1;
                } else {
                    button.classList.remove('liked');
                    button.querySelector('i').classList.replace('fas', 'far');
                    likeCount.textContent = parseInt(likeCount.textContent) - 1;
                }
                showNotification('Une erreur est survenue. Veuillez réessayer.', 'error');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            showNotification('Une erreur de connexion est survenue.', 'error');
        });
    }
    
    // Gestion de la suppression de commentaire
    else if (e.target.closest('.delete-comment')) {
        e.preventDefault();
        const button = e.target.closest('.delete-comment');
        const commentId = button.dataset.commentId;
        
        if (confirm('Êtes-vous sûr de vouloir supprimer ce commentaire ? Cette action est irréversible.')) {
            fetch(`/comment/${commentId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const commentElement = document.getElementById(`comment-${commentId}`);
                    if (commentElement) {
                        // Si c'est un commentaire parent, on le supprime complètement
                        if (commentElement.classList.contains('comment')) {
                            commentElement.remove();
                        } 
                        // Si c'est une réponse, on marque simplement comme supprimé
                        else {
                            commentElement.querySelector('.comment-text').textContent = 'Commentaire supprimé';
                            commentElement.querySelector('.comment-actions').remove();
                            commentElement.classList.add('deleted-comment');
                        }
                    }
                    showNotification('Commentaire supprimé avec succès.', 'success');
                } else {
                    showNotification(data.error || 'Une erreur est survenue lors de la suppression du commentaire.', 'error');
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                showNotification('Une erreur de connexion est survenue.', 'error');
            });
        }
    }
    
    // Gestion de l'édition de commentaire
    else if (e.target.closest('.edit-comment')) {
        e.preventDefault();
        const button = e.target.closest('.edit-comment');
        const commentId = button.dataset.commentId;
        const commentElement = document.getElementById(`comment-${commentId}`);
        
        // Récupérer le contenu actuel du commentaire
        const currentText = commentElement.querySelector('.comment-text').textContent;
        
        // Créer le formulaire d'édition
        const formHtml = `
            <div class="comment-edit-form">
                <form method="POST" action="/comment/${commentId}/edit/" class="edit-comment-form">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                    <div class="form-group">
                        <textarea name="text" class="form-control" rows="3" required>${currentText}</textarea>
                    </div>
                    <div class="d-flex justify-content-end mt-2">
                        <button type="button" class="btn btn-sm btn-outline-secondary me-2 cancel-edit">Annuler</button>
                        <button type="submit" class="btn btn-sm btn-primary">Enregistrer</button>
                    </div>
                </form>
            </div>
        `;
        
        // Remplacer le contenu du commentaire par le formulaire
        commentElement.querySelector('.comment-content').innerHTML = formHtml;
        
        // Mettre le focus sur le textarea
        commentElement.querySelector('textarea').focus();
    }
    
    // Annulation de l'édition
    else if (e.target.closest('.cancel-edit')) {
        const button = e.target.closest('.cancel-edit');
        const commentForm = button.closest('.comment-edit-form');
        const commentId = commentForm.closest('.comment').id.replace('comment-', '');
        
        // Recharger le commentaire depuis le serveur
        fetch(`/comment/${commentId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const commentElement = document.getElementById(`comment-${commentId}`);
                    commentElement.querySelector('.comment-content').innerHTML = data.html;
                }
            });
    }
    
    // Gestion de la soumission du formulaire d'édition
    else if (e.target.closest('.edit-comment-form')) {
        e.preventDefault();
        const form = e.target.closest('.edit-comment-form');
        const formData = new FormData(form);
        const commentId = form.closest('.comment').id.replace('comment-', '');
        
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const commentElement = document.getElementById(`comment-${commentId}`);
                commentElement.querySelector('.comment-text').textContent = data.new_text;
                
                // Mettre à jour la date de modification si elle existe
                if (data.updated_at) {
                    let editedBadge = commentElement.querySelector('.edited-badge');
                    if (!editedBadge) {
                        editedBadge = document.createElement('span');
                        editedBadge.className = 'text-muted small ms-2 edited-badge';
                        commentElement.querySelector('.comment-meta').appendChild(editedBadge);
                    }
                    editedBadge.textContent = `modifié ${data.updated_at}`;
                }
                
                showNotification('Commentaire mis à jour avec succès', 'success');
            } else {
                showNotification(data.error || 'Une erreur est survenue lors de la mise à jour du commentaire.', 'error');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            showNotification('Une erreur de connexion est survenue.', 'error');
        });
    }
    
    // Gestion du signalement de commentaire
    else if (e.target.closest('.report-comment')) {
        e.preventDefault();
        const button = e.target.closest('.report-comment');
        const commentId = button.dataset.commentId;
        
        if (confirm('Signaler ce commentaire comme inapproprié ?')) {
            fetch(`/comment/${commentId}/report/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Commentaire signalé avec succès. Notre équipe va examiner ce contenu.', 'success');
                } else {
                    showNotification(data.error || 'Une erreur est survenue lors du signalement du commentaire.', 'error');
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                showNotification('Une erreur de connexion est survenue.', 'error');
            });
        }
    }
    
    // Gestion de l'affichage des réponses
    else if (e.target.closest('.view-replies-btn')) {
        e.preventDefault();
        const button = e.target.closest('.view-replies-btn');
        const commentId = button.dataset.commentId;
        const repliesContainer = document.getElementById(`replies-${commentId}`);
        
        if (repliesContainer.classList.contains('d-none')) {
            // Charger les réponses si ce n'est pas déjà fait
            if (!repliesContainer.hasChildNodes()) {
                fetch(`/comment/${commentId}/replies/`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            repliesContainer.innerHTML = data.replies_html;
                            repliesContainer.classList.remove('d-none');
                            button.innerHTML = '<i class="fas fa-chevron-up"></i> Masquer les réponses';
                        }
                    });
            } else {
                repliesContainer.classList.remove('d-none');
                button.innerHTML = '<i class="fas fa-chevron-up"></i> Masquer les réponses';
            }
        } else {
            repliesContainer.classList.add('d-none');
            button.innerHTML = '<i class="fas fa-chevron-down"></i> Voir les réponses';
        }
    }
});

// Fonction utilitaire pour récupérer un cookie par son nom
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

// Initialisation des tooltips Bootstrap
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Gestion du chargement automatique des images
    document.querySelectorAll('.comment-image-preview').forEach(img => {
        img.onload = function() {
            this.parentElement.classList.add('loaded');
        };
    });
});
