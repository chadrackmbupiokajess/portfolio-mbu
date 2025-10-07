from .models import Category, Tag, PortfolioStats, Resume, Notification
from django.db.models import Count

def global_context(request):
    """
    Context processor pour fournir des données globales à tous les templates
    """
    # Catégories avec nombre de projets
    categories = Category.objects.annotate(
        project_count=Count('project')
    ).filter(project_count__gt=0)
    
    # Tags populaires
    popular_tags = Tag.objects.annotate(
        project_count=Count('project')
    ).filter(project_count__gt=0).order_by('-project_count')[:10]
    
    # Statistiques du portfolio
    try:
        stats = PortfolioStats.objects.first()
        if not stats:
            stats = PortfolioStats.objects.create()
    except:
        stats = None
    
    # CV actifs
    active_resumes = Resume.objects.filter(is_active=True)
    
    return {
        'global_categories': categories,
        'global_popular_tags': popular_tags,
        'global_stats': stats,
        'global_resumes': active_resumes,
    }

def unread_notifications_count(request):
    """
    Context processor pour le nombre de notifications non lues
    """
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        unread_count = 0
    
    return {
        'unread_notifications_count': unread_count
    }