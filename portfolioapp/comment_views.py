from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Count

from .models import Project, Comment, Notification
from .forms import CommentForm, ReplyForm

@login_required
def toggle_like_comment(request, comment_id):
    """Vue pour liker/unliker un commentaire"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
        
        # Créer une notification pour l'auteur du commentaire
        if comment.author != request.user:
            Notification.objects.create(
                user=comment.author,
                message=f"{request.user.username} a aimé votre commentaire",
                link=f"{reverse('project_detail', args=[comment.project.id])}#comment-{comment.id}"
            )
    
    return JsonResponse({
        'success': True,
        'liked': liked,
        'likes_count': comment.likes.count()
    })

@login_required
def delete_comment(request, comment_id):
    """Vue pour supprimer un commentaire ou une réponse"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Vérifier que l'utilisateur est l'auteur du commentaire ou un administrateur
    if comment.author != request.user and not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'Vous n\'êtes pas autorisé à effectuer cette action.'
        }, status=403)
    
    # Marquer le commentaire comme supprimé au lieu de le supprimer réellement
    comment.is_deleted = True
    comment.text = "Ce commentaire a été supprimé."
    comment.save(update_fields=['is_deleted', 'text'])
    
    return JsonResponse({
        'success': True,
        'message': 'Commentaire supprimé avec succès.'
    })

@login_required
def edit_comment(request, comment_id):
    """Vue pour éditer un commentaire ou une réponse"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Vérifier que l'utilisateur est l'auteur du commentaire
    if comment.author != request.user:
        return JsonResponse({
            'success': False,
            'error': 'Vous n\'êtes pas autorisé à modifier ce commentaire.'
        }, status=403)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.is_edited = True
            comment.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Commentaire mis à jour avec succès.',
                'new_text': comment.text,
                'updated_at': comment.updated_at.strftime('%d/%m/%Y à %H:%M')
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    # Renvoyer le formulaire d'édition
    form = CommentForm(instance=comment)
    return render(request, 'portfolioapp/comment_edit_form.html', {
        'form': form,
        'comment': comment
    })

def get_replies(request, comment_id):
    """Récupère les réponses à un commentaire"""
    comment = get_object_or_404(Comment, id=comment_id)
    replies = comment.get_replies()
    
    replies_html = ''
    for reply in replies:
        replies_html += render_to_string('portfolioapp/comment_item.html', {
            'comment': reply,
            'user': request.user,
            'is_reply': True
        })
    
    return JsonResponse({
        'success': True,
        'replies_html': replies_html,
        'replies_count': replies.count()
    })

@login_required
def report_comment(request, comment_id):
    """Signaler un commentaire inapproprié"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Vérifier que l'utilisateur ne signale pas son propre commentaire
    if comment.author == request.user:
        return JsonResponse({
            'success': False,
            'error': 'Vous ne pouvez pas signaler votre propre commentaire.'
        }, status=400)
    
    # Ici, vous pourriez implémenter une logique pour enregistrer le signalement
    # Par exemple, en créant un modèle Report ou en incrémentant un compteur
    
    return JsonResponse({
        'success': True,
        'message': 'Commentaire signalé avec succès. Notre équipe va examiner ce contenu.'
    })
