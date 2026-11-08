from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils.text import slugify
from django.urls import reverse
from .models import (Project, Comment, Reply, Notification, Category, About,
                     Tag, ProjectLike, Testimonial, Resume, BlogPost, PortfolioStats, Profile)
from .forms import (CommentForm, ReplyForm, ProfileForm, ContactForm, 
                   TestimonialForm, ProjectSearchForm)

def home(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'portfolioapp/home.html', {'projects': projects})

def blog(request):
    return render(request, 'portfolioapp/blog.html')

def projects_view(request):
    all_projects = Project.objects.all().order_by('-created_at')
    projects = all_projects
    categories = Category.objects.annotate(num_projects=Count('project')).order_by('name')
    category_filter = request.GET.get('category')
    if category_filter and category_filter != 'all':
        if category_filter == 'uncategorized':
            projects = projects.filter(category__isnull=True)
        else:
            try:
                projects = projects.filter(category_id=int(category_filter))
            except ValueError:
                category_filter = None
    return render(request, 'portfolioapp/projects.html', {
        'projects': projects,
        'categories': categories,
        'total_count': all_projects.count(),
        'uncategorized_count': all_projects.filter(category__isnull=True).count(),
        'active_category': category_filter,
    })


# Vue pour la page de détail d'un projet
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Compter la visite (une fois par session et par projet)
    seen = request.session.get('seen_projects', [])
    if project.pk not in seen:
        project.increment_views()
        seen.append(project.pk)
        request.session['seen_projects'] = seen[-200:]

    # Commentaires de premier niveau (les réponses sont affichées sous leur parent)
    comments = (Comment.objects
                .filter(project=project, parent__isnull=True, is_deleted=False)
                .select_related('author', 'author__profile')
                .order_by('-created_at'))
    comments_count = Comment.objects.filter(project=project, is_deleted=False).count()

    # Autres projets : même catégorie d'abord, puis les plus récents
    related_projects = list(Project.objects.filter(category=project.category)
                            .exclude(pk=project.pk).order_by('-created_at')[:3]) if project.category else []
    if len(related_projects) < 3:
        exclude_ids = [project.pk] + [p.pk for p in related_projects]
        related_projects += list(Project.objects.exclude(pk__in=exclude_ids)
                                 .order_by('-created_at')[:3 - len(related_projects)])

    return render(request, 'portfolioapp/project_detail.html', {
        'project': project,
        'comments': comments,
        'comments_count': comments_count,
        'related_projects': related_projects,
        'is_liked': request.user.is_authenticated and ProjectLike.objects.filter(project=project, user=request.user).exists(),
    })


# Vue pour ajouter un commentaire
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Comment, Reply
from .forms import CommentForm, ReplyForm

@login_required
def add_comment(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.project = project
            comment.author = request.user
            comment.save()
            
            # Créer une notification pour le propriétaire du projet
            if project.user != request.user:
                Notification.objects.create(
                    user=project.user,
                    message=f"{request.user.username} a commenté votre projet {project.title}",
                    link=reverse('project_detail', args=[project.id]) + f"#comment-{comment.id}"
                )
            
            if request.headers.get('x-requested-with') != 'XMLHttpRequest':
                return redirect(reverse('project_detail', args=[project.id]) + f"#comment-{comment.id}")

            # Rendre le template du commentaire en HTML
            comment_html = render_to_string('portfolioapp/comment_item.html', {
                'comment': comment,
                'user': request.user
            }, request=request)
            return JsonResponse({
                'success': True, 
                'comment_html': comment_html,
                'comment_id': comment.id
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'errors': 'Méthode non autorisée'})

@login_required
def add_reply(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        form = ReplyForm(request.POST, request.FILES)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.comment = comment
            reply.author = request.user
            reply.project = comment.project
            reply.parent = comment
            reply.save()
            
            # Créer une notification pour l'auteur du commentaire
            if comment.author != request.user:
                Notification.objects.create(
                    user=comment.author,
                    message=f"{request.user.username} a répondu à votre commentaire",
                    link=reverse('project_detail', args=[comment.project.id]) + f"#comment-{comment.id}"
                )
            
            if request.headers.get('x-requested-with') != 'XMLHttpRequest':
                return redirect(reverse('project_detail', args=[comment.project.id]) + f"#comment-{reply.id}")

            # Rendre le template de la réponse en HTML
            reply_html = render_to_string('portfolioapp/comment_item.html', {
                'comment': reply,
                'user': request.user,
                'is_reply': True
            }, request=request)
            return JsonResponse({
                'success': True, 
                'reply_html': reply_html,
                'reply_id': reply.id
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'errors': 'Méthode non autorisée'})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé pour {username} ! Vous pouvez maintenant vous connecter.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def profile(request):
    profile = request.user.profile
    return render(request, 'registration/profile.html', {'profile': profile})

@login_required
def edit_profile(request):
    # S'assurer que l'utilisateur a un profil
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!')
            return redirect('profile')
        else:
            messages.error(request, 'Erreur lors de la mise à jour du profil. Veuillez vérifier les champs.')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'registration/edit_profile.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('home')

@login_required
def get_unread_notifications_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})

@login_required
def view_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'portfolioapp/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    return redirect(notification.link)

@login_required
def mark_all_notifications_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('view_notifications')

def about(request):
    about_info = About.objects.first()
    return render(request, 'portfolioapp/about.html', {'about_info': about_info})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre message a été envoyé avec succès!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'portfolioapp/contact.html', {'form': form})

# Nouvelles vues pour les fonctionnalités ajoutées

@login_required
def toggle_like(request, project_id):
    """Vue pour liker/unliker un projet"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    project = get_object_or_404(Project, id=project_id)
    like, created = ProjectLike.objects.get_or_create(user=request.user, project=project)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    likes_count = project.likes.count()
    return JsonResponse({'success': True, 'liked': liked, 'likes_count': likes_count})

def search_projects(request):
    """Vue pour la recherche avancée de projets"""
    form = ProjectSearchForm(request.GET)
    projects = Project.objects.all()
    
    if form.is_valid():
        search_query = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        tag = form.cleaned_data.get('tag')
        status = form.cleaned_data.get('status')
        
        if search_query:
            projects = projects.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(technologies__icontains=search_query)
            )
        
        if category:
            projects = projects.filter(category=category)
        
        if tag:
            projects = projects.filter(tags=tag)
        
        if status:
            projects = projects.filter(status=status)
    
    # Pagination
    paginator = Paginator(projects, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'portfolioapp/search_results.html', {
        'form': form,
        'page_obj': page_obj,
        'projects': page_obj,
    })

def blog_list(request):
    """Vue pour la liste des articles de blog"""
    # Les administrateurs voient aussi leurs brouillons (marqués « Brouillon »)
    if request.user.is_staff:
        posts = BlogPost.objects.all()
    else:
        posts = BlogPost.objects.filter(is_published=True)
    
    # Recherche
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    # Filtrage par tag
    tag_id = request.GET.get('tag')
    if tag_id:
        posts = posts.filter(tags__id=tag_id)
    
    # Pagination
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Tags populaires
    popular_tags = Tag.objects.annotate(
        blog_count=Count('blogpost')
    ).filter(blog_count__gt=0).order_by('-blog_count')[:10]
    
    return render(request, 'portfolioapp/blog_list.html', {
        'page_obj': page_obj,
        'popular_tags': popular_tags,
        'search_query': search_query,
    })

def blog_detail(request, slug):
    """Vue pour le détail d'un article de blog"""
    if request.user.is_staff:
        post = get_object_or_404(BlogPost, slug=slug)
    else:
        post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    if post.is_published:
        post.increment_views()
    
    # Articles similaires
    related_posts = BlogPost.objects.filter(
        is_published=True,
        tags__in=post.tags.all()
    ).exclude(id=post.id).distinct()[:3]
    
    return render(request, 'portfolioapp/blog_detail.html', {
        'post': post,
        'related_posts': related_posts,
    })

def testimonials_view(request):
    """Vue pour afficher les témoignages"""
    testimonials = Testimonial.objects.all().order_by('-created_at')
    featured_testimonials = testimonials.filter(is_featured=True)[:3]
    
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Merci pour votre témoignage! Il sera publié après validation.')
            return redirect('testimonials')
    else:
        form = TestimonialForm()
    
    return render(request, 'portfolioapp/testimonials.html', {
        'testimonials': testimonials,
        'featured_testimonials': featured_testimonials,
        'form': form,
    })

def download_resume(request, resume_id):
    """Vue pour télécharger un CV"""
    resume = get_object_or_404(Resume, id=resume_id, is_active=True)
    resume.increment_downloads()
    
    response = HttpResponse(resume.file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{resume.title}.pdf"'
    return response

def portfolio_stats(request):
    """Vue pour afficher les statistiques du portfolio"""
    stats, created = PortfolioStats.objects.get_or_create(id=1)
    
    # Mettre à jour les statistiques
    stats.total_projects = Project.objects.count()
    stats.total_blog_posts = BlogPost.objects.filter(is_published=True).count()
    stats.total_views = (
        sum(Project.objects.values_list('views_count', flat=True)) +
        sum(BlogPost.objects.values_list('views_count', flat=True))
    )
    stats.total_likes = ProjectLike.objects.count()
    stats.save()
    
    # Projets les plus populaires
    popular_projects = Project.objects.order_by('-views_count')[:5]
    
    # Articles les plus populaires
    popular_posts = BlogPost.objects.filter(is_published=True).order_by('-views_count')[:5]
    
    # Projets récents
    recent_projects = Project.objects.order_by('-created_at')[:5]
    
    return render(request, 'portfolioapp/stats.html', {
        'stats': stats,
        'popular_projects': popular_projects,
        'popular_posts': popular_posts,
        'recent_projects': recent_projects,
    })

def privacy_policy(request):
    """Vue pour la politique de confidentialité"""
    return render(request, 'portfolioapp/privacy_policy.html')

def terms_of_service(request):
    """Vue pour les conditions d'utilisation"""
    return render(request, 'portfolioapp/terms_of_service.html')

# =========================================================================
# Galerie photos + fichiers lus par les moteurs de recherche et les IA
# =========================================================================
import json
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags
from django.templatetags.static import static as static_url
from .models import GalleryPhoto

SITE_OWNER = "Chadrack Mbu Jess"
ROBOTS_DISALLOW = [
    '/admin/', '/accounts/', '/login/', '/signup/', '/logout/', '/profile/',
    '/notifications/', '/notification/', '/unread-notifications/',
    '/mark-all-notifications-as-read/', '/comment/', '/stats/', '/download-resume/',
]
# Robots des moteurs de recherche et des assistants IA explicitement autorisés
ALLOWED_BOTS = [
    'Googlebot', 'Googlebot-Image', 'Google-Extended', 'Bingbot', 'DuckDuckBot', 'YandexBot', 'Applebot', 'Applebot-Extended',
    'GPTBot', 'OAI-SearchBot', 'ChatGPT-User',
    'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'anthropic-ai',
    'PerplexityBot', 'Perplexity-User', 'CCBot', 'Meta-ExternalAgent', 'MistralAI-User', 'cohere-ai',
]


def _jsonld(data):
    """Bloc JSON-LD sûr à insérer dans une balise <script>."""
    text = json.dumps(data, ensure_ascii=False, indent=2)
    text = text.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return mark_safe(text)


def _abs(request, path):
    return request.build_absolute_uri(path)


def _person(request):
    return {
        "@type": "Person",
        "name": SITE_OWNER,
        "url": _abs(request, reverse('home')),
        "image": _abs(request, static_url('images/chadrack-mbu-jess.jpg')),
    }


def _image_object(request, photo, full=False):
    data = {
        "@type": "ImageObject",
        "contentUrl": _abs(request, photo.image.url),
        "url": _abs(request, photo.get_absolute_url()),
        "name": photo.title,
        "caption": photo.alt_text,
        "creator": _person(request),
        "creditText": SITE_OWNER,
        "copyrightNotice": f"© {SITE_OWNER}",
        "license": _abs(request, reverse('terms_of_service')),
        "acquireLicensePage": _abs(request, reverse('contact')),
    }
    if photo.width and photo.height:
        data["width"] = photo.width
        data["height"] = photo.height
    if full:
        if photo.description:
            data["description"] = photo.description
        if photo.taken_at:
            data["dateCreated"] = photo.taken_at.isoformat()
        data["datePublished"] = photo.created_at.date().isoformat()
        if photo.location:
            data["contentLocation"] = {"@type": "Place", "name": photo.location}
        if photo.keyword_list:
            data["keywords"] = ", ".join(photo.keyword_list)
    return data


def gallery(request):
    """Liste des photos publiées, filtrable par album."""
    photos = GalleryPhoto.objects.filter(is_published=True)
    albums = (GalleryPhoto.objects.filter(is_published=True).exclude(album='')
              .order_by('album').values_list('album', flat=True).distinct())
    active_album = request.GET.get('album') or ''
    if active_album:
        photos = photos.filter(album=active_album)

    paginator = Paginator(photos, 24)
    page_obj = paginator.get_page(request.GET.get('page'))

    jsonld = _jsonld({
        "@context": "https://schema.org",
        "@type": "ImageGallery",
        "name": f"Galerie de {SITE_OWNER}",
        "url": _abs(request, reverse('gallery')),
        "author": _person(request),
        "associatedMedia": [_image_object(request, p) for p in page_obj],
    })
    return render(request, 'portfolioapp/gallery.html', {
        'page_obj': page_obj,
        'albums': albums,
        'active_album': active_album,
        'total_count': GalleryPhoto.objects.filter(is_published=True).count(),
        'jsonld': jsonld,
    })


def gallery_detail(request, slug):
    """Page d'une photo : grande image, texte, informations et photos voisines."""
    photo = get_object_or_404(GalleryPhoto, slug=slug, is_published=True)
    ordered = list(GalleryPhoto.objects.filter(is_published=True).values_list('slug', flat=True))
    idx = ordered.index(photo.slug)
    prev_slug = ordered[idx - 1] if idx > 0 else None
    next_slug = ordered[idx + 1] if idx < len(ordered) - 1 else None
    prev_photo = GalleryPhoto.objects.filter(slug=prev_slug).first() if prev_slug else None
    next_photo = GalleryPhoto.objects.filter(slug=next_slug).first() if next_slug else None

    related = GalleryPhoto.objects.filter(is_published=True).exclude(pk=photo.pk)
    if photo.album:
        related = related.filter(album=photo.album)
    related = related[:6]

    data = {"@context": "https://schema.org"}
    data.update(_image_object(request, photo, full=True))
    return render(request, 'portfolioapp/gallery_detail.html', {
        'photo': photo,
        'prev_photo': prev_photo,
        'next_photo': next_photo,
        'related_photos': related,
        'jsonld': _jsonld(data),
    })


def robots_txt(request):
    lines = ["# Robots des moteurs de recherche et des assistants IA : bienvenue."]
    lines += [f"User-agent: {bot}" for bot in ALLOWED_BOTS]
    lines += ["User-agent: *", "Allow: /"]
    lines += [f"Disallow: {path}" for path in ROBOTS_DISALLOW]
    lines += ["", f"Sitemap: {_abs(request, reverse('sitemap_xml'))}", ""]
    return HttpResponse("\n".join(lines), content_type='text/plain; charset=utf-8')


def sitemap_xml(request):
    """Plan du site avec les images (Google Images)."""
    def entry(path, lastmod=None, images=None, priority='0.5'):
        return {
            'loc': _abs(request, path),
            'lastmod': lastmod.date().isoformat() if hasattr(lastmod, 'date') else None,
            'images': [_abs(request, i) for i in (images or [])],
            'priority': priority,
        }

    about = About.objects.first()
    urls = [
        entry(reverse('home'), images=[static_url('images/chadrack-mbu-jess-og.jpg')], priority='1.0'),
        entry(reverse('about'), images=[about.photo.url] if about and about.photo else [static_url('images/chadrack-mbu-jess.jpg')], priority='0.8'),
        entry(reverse('projects'), priority='0.9'),
        entry(reverse('gallery'), priority='0.8'),
        entry(reverse('blog'), priority='0.7'),
        entry(reverse('testimonials'), priority='0.5'),
        entry(reverse('contact'), priority='0.6'),
        entry(reverse('privacy_policy'), priority='0.2'),
        entry(reverse('terms_of_service'), priority='0.2'),
    ]
    for p in Project.objects.all():
        urls.append(entry(reverse('project_detail', args=[p.pk]), p.updated_at, [p.image.url] if p.image else [], '0.8'))
    for post in BlogPost.objects.filter(is_published=True).exclude(slug=''):
        urls.append(entry(reverse('blog_detail', args=[post.slug]), post.updated_at, [post.image.url] if post.image else [], '0.6'))
    for photo in GalleryPhoto.objects.filter(is_published=True):
        urls.append(entry(photo.get_absolute_url(), photo.updated_at, [photo.image.url], '0.6'))

    return render(request, 'portfolioapp/seo/sitemap.xml', {'urls': urls},
                  content_type='application/xml; charset=utf-8')


def llms_txt(request):
    """Résumé du site au format llms.txt, destiné aux assistants IA."""
    projects = Project.objects.all().order_by('-created_at')
    posts = BlogPost.objects.filter(is_published=True).exclude(slug='')[:30]
    photos = GalleryPhoto.objects.filter(is_published=True)[:60]
    about = About.objects.first()
    about_text = strip_tags(about.description).strip() if about and about.description else ''
    return render(request, 'portfolioapp/seo/llms.txt', {
        'projects': projects,
        'posts': posts,
        'photos': photos,
        'about_text': about_text,
        'base': _abs(request, '/').rstrip('/'),
    }, content_type='text/plain; charset=utf-8')
