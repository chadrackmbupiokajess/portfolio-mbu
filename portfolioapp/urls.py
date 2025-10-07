from django.urls import path
from . import views
from .comment_views import (
    toggle_like_comment, delete_comment, edit_comment,
    get_replies, report_comment
)
from .views import (custom_logout, get_unread_notifications_count, view_notifications, 
                   mark_all_notifications_as_read, mark_notification_as_read, toggle_like,
                   search_projects, blog_list, blog_detail, testimonials_view, 
                   download_resume, portfolio_stats)

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Projets
    path('projects/', views.projects_view, name='projects'),
    path('projets/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail_en'),
    path('search/', search_projects, name='search_projects'),
    path('project/<int:project_id>/like/', toggle_like, name='toggle_like'),
    
    # Commentaires
    path('projets/<int:project_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
    path('comment/<int:comment_id>/like/', toggle_like_comment, name='toggle_like_comment'),
    path('comment/<int:comment_id>/delete/', delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/edit/', edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/replies/', get_replies, name='get_replies'),
    path('comment/<int:comment_id>/report/', report_comment, name='report_comment'),
    
    # Blog
    path('blog/', blog_list, name='blog'),
    path('blog/<slug:slug>/', blog_detail, name='blog_detail'),
    
    # Témoignages
    path('testimonials/', testimonials_view, name='testimonials'),
    
    # CV
    path('download-resume/<int:resume_id>/', download_resume, name='download_resume'),
    
    # Statistiques
    path('stats/', portfolio_stats, name='portfolio_stats'),
    
    # Authentification et profil
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('logout/', custom_logout, name='logout'),
    
    # Notifications
    path('unread-notifications/', get_unread_notifications_count, name='unread_notifications'),
    path('notifications/', view_notifications, name='view_notifications'),
    path('notification/mark-as-read/<int:notification_id>/', mark_notification_as_read, name='mark_notification_as_read'),
    path('mark-all-notifications-as-read/', mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
    
    # Pages légales
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
]