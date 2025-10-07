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
    projects = Project.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    category_icons = {
        "Développement": "bi-code",
        "Design": "bi-brush",
        "Marketing": "bi-megaphone",
        "IA": "bi-cpu",
        "Gestion de Base de données": "bi-database",
        "Automatisation": "bi-robot",
        "Ecole": "bi-building",
        "Portfolio": "bi-briefcase",
        "App Desktop": "bi-laptop",
        "App Web": "bi-globe",
        "Aide": "bi-life-preserver",
        "Eglise": "bi-house-door",
        "TV": "bi-tv",
    }
    category_filter = request.GET.get('category')
    if category_filter:
        if category_filter == 'all':
            pass
        elif category_filter == 'uncategorized':
            projects = projects.filter(category__isnull=True)
        else:
            try:
                category_id = int(category_filter)
                projects = projects.filter(category_id=category_id)
            except ValueError:
                pass
    for project in projects:
        if not project.image:
            project.image_url = '/static/images/default.jpg'
        else:
            project.image_url = project.image.url
    return render(request, 'portfolioapp/projects.html', {
        'projects': projects,
        'categories': categories,
        'category_icons': category_icons,
    })


# Vue pour la page de détail d'un projet
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Récupérer les commentaires triés par date de création décroissante
    comments = Comment.objects.filter(project=project).order_by('-created_at')

    # Récupérer les catégories et les projets associés
    categories = Category.objects.all()
    categories_with_projects = [category for category in categories if
                                Project.objects.filter(category=category).exists()]
    projects_by_category = {category: Project.objects.filter(category=category) for category in
                            categories_with_projects}

    # Récupérer les projets non catégorisés
    uncategorized_projects = Project.objects.filter(category__isnull=True)
    if uncategorized_projects.exists():
        projects_by_category["non_categorise"] = uncategorized_projects

    # Gestion des formulaires de commentaire et de réponse
    if request.method == 'POST':
        # Gestion de l'ajout de commentaire
        if 'comment_form' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.project = project
                comment.author = request.user
                comment.save()
                return redirect('project_detail', pk=project.id)

        # Gestion de l'ajout de réponse
        elif 'reply_form' in request.POST:
            reply_form = ReplyForm(request.POST)
            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                comment_id = request.POST.get('comment_id')
                comment = get_object_or_404(Comment, id=comment_id)
                reply.comment = comment
                reply.author = request.user
                reply.save()
                return redirect('project_detail', pk=comment.project.id)
    else:
        form = CommentForm()
        reply_form = ReplyForm()

    return render(request, 'portfolioapp/project_detail.html', {
        'project': project,
        'comments': comments,
        'projects_by_category': projects_by_category,
        'categories': categories_with_projects,
        'form': form,
        'reply_form': reply_form,
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
            
            # Rendre le template du commentaire en HTML
            comment_html = render_to_string('portfolioapp/comment_item.html', {
                'comment': comment,
                'user': request.user
            })
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
            
            # Rendre le template de la réponse en HTML
            reply_html = render_to_string('portfolioapp/comment_item.html', {
                'comment': reply,
                'user': request.user,
                'is_reply': True
            })
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
    project = get_object_or_404(Project, id=project_id)
    like, created = ProjectLike.objects.get_or_create(user=request.user, project=project)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    likes_count = project.likes.count()
    return JsonResponse({'liked': liked, 'likes_count': likes_count})

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
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
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