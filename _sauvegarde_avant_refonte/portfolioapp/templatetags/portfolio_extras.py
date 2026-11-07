from django import template
from django.utils.safestring import mark_safe
from django.db.models import Count
from ..models import Project, BlogPost, Tag, ProjectLike, AdUnit, AdSenseConfig
import json

register = template.Library()

@register.filter
def split_technologies(technologies):
    """Divise les technologies par virgule et retourne une liste"""
    if technologies:
        return [tech.strip() for tech in technologies.split(',')]
    return []

@register.filter
def is_liked_by(project, user):
    """Vérifie si un projet est liké par un utilisateur"""
    if user.is_authenticated:
        return ProjectLike.objects.filter(project=project, user=user).exists()
    return False

@register.filter
def get_range(value):
    """Retourne une range pour les boucles dans les templates"""
    return range(value)

@register.simple_tag
def get_popular_projects(limit=5):
    """Retourne les projets les plus populaires"""
    return Project.objects.order_by('-views_count', '-created_at')[:limit]

@register.simple_tag
def get_recent_blog_posts(limit=3):
    """Retourne les articles de blog récents"""
    return BlogPost.objects.filter(is_published=True).order_by('-published_date')[:limit]

@register.simple_tag
def get_featured_projects(limit=6):
    """Retourne les projets mis en avant"""
    return Project.objects.filter(featured=True).order_by('-created_at')[:limit]

@register.inclusion_tag('portfolioapp/tags/project_card.html')
def project_card(project, show_actions=True):
    """Template tag pour afficher une carte de projet"""
    return {
        'project': project,
        'show_actions': show_actions,
    }

@register.inclusion_tag('portfolioapp/tags/blog_card.html')
def blog_card(post):
    """Template tag pour afficher une carte d'article de blog"""
    return {
        'post': post,
    }

@register.filter
def json_encode(value):
    """Encode une valeur en JSON pour JavaScript"""
    return mark_safe(json.dumps(value))

@register.simple_tag
def get_tag_cloud():
    """Retourne un nuage de tags avec leurs compteurs"""
    return Tag.objects.annotate(
        usage_count=Count('project') + Count('blogpost')
    ).filter(usage_count__gt=0).order_by('-usage_count')

@register.filter
def multiply(value, arg):
    """Multiplie deux valeurs"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    """Calcule le pourcentage"""
    try:
        if total == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError):
        return 0

@register.simple_tag(takes_context=True)
def query_string(context, **kwargs):
    """Génère une query string en préservant les paramètres existants"""
    request = context['request']
    query_dict = request.GET.copy()
    
    for key, value in kwargs.items():
        if value is not None:
            query_dict[key] = value
        elif key in query_dict:
            del query_dict[key]
    
    return query_dict.urlencode()

@register.filter
def truncate_chars(value, length):
    """Tronque un texte à un nombre de caractères donné"""
    if len(value) <= length:
        return value
    return value[:length] + '...'

# ===== TEMPLATE TAGS GOOGLE ADSENSE =====

@register.simple_tag(takes_context=True)
def adsense_unit(context, position):
    """Affiche une unité publicitaire AdSense pour une position donnée"""
    request = context.get('request')
    if not request:
        return ''
    
    current_path = request.path
    
    # Récupérer les unités publicitaires pour cette position
    ad_units = AdUnit.objects.filter(
        position=position,
        is_active=True
    )
    
    # Filtrer selon le type d'appareil
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone', 'ipad'])
    
    if is_mobile:
        ad_units = ad_units.filter(show_on_mobile=True)
    else:
        ad_units = ad_units.filter(show_on_desktop=True)
    
    # Filtrer selon la page actuelle
    valid_ads = []
    for ad_unit in ad_units:
        if ad_unit.should_display_on_page(current_path):
            valid_ads.append(ad_unit)
    
    if not valid_ads:
        return ''
    
    # Prendre la première unité valide (ou implémenter une logique de rotation)
    ad_unit = valid_ads[0]
    
    return mark_safe(ad_unit.get_ad_code())

@register.simple_tag
def adsense_script():
    """Génère le script principal AdSense"""
    config = AdSenseConfig.get_config()
    
    if not config.is_active:
        return ''
    
    script = f'''
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={config.publisher_id}"
            crossorigin="anonymous"></script>
    '''
    
    return mark_safe(script.strip())

@register.simple_tag
def adsense_auto_ads():
    """Génère le code pour les Auto Ads"""
    config = AdSenseConfig.get_config()
    
    if not config.is_active:
        return ''
    
    # Vérifier s'il y a des unités Auto Ads actives
    has_auto_ads = AdUnit.objects.filter(
        ad_type='auto',
        is_active=True
    ).exists()
    
    if not has_auto_ads:
        return ''
    
    script = f'''
    <script>
        (adsbygoogle = window.adsbygoogle || []).push({{
            google_ad_client: "{config.publisher_id}",
            enable_page_level_ads: true
        }});
    </script>
    '''
    
    return mark_safe(script.strip())

@register.inclusion_tag('portfolioapp/tags/adsense_banner.html', takes_context=True)
def adsense_banner(context, position, css_class=''):
    """Template tag d'inclusion pour afficher une bannière publicitaire"""
    request = context.get('request')
    if not request:
        return {'ad_code': '', 'css_class': css_class}
    
    current_path = request.path
    
    # Récupérer l'unité publicitaire
    try:
        ad_unit = AdUnit.objects.filter(
            position=position,
            is_active=True
        ).first()
        
        if ad_unit and ad_unit.should_display_on_page(current_path):
            # Vérifier le type d'appareil
            user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
            is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone', 'ipad'])
            
            if (is_mobile and ad_unit.show_on_mobile) or (not is_mobile and ad_unit.show_on_desktop):
                return {
                    'ad_code': ad_unit.get_ad_code(),
                    'css_class': css_class,
                    'custom_css': ad_unit.custom_css,
                    'position': position
                }
    except AdUnit.DoesNotExist:
        pass
    
    return {'ad_code': '', 'css_class': css_class}

@register.simple_tag
def adsense_config():
    """Récupère la configuration AdSense"""
    return AdSenseConfig.get_config()

@register.filter
def is_adsense_active(value):
    """Vérifie si AdSense est actif"""
    config = AdSenseConfig.get_config()
    return config.is_active