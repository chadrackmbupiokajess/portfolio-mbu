# portfolio/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),  # URL de connexion
    #path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # URL de déconnexion
    path('', include('portfolioapp.urls')),
    path('accounts/', include('allauth.urls')),  # URLs de django-allauth
    path('ckeditor5/', include('django_ckeditor_5.urls')),  # Utilisez 'django_ckeditor_5.urls'

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)