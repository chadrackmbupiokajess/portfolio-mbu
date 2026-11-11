from django.contrib import admin
from django.utils.html import format_html
from . models import *

# Configuration personnalisée pour les modèles

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_preview', 'projects_count']
    search_fields = ['name']
    
    def color_preview(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 2px 8px; border-radius: 3px; color: white;">{}</span>',
            obj.color, obj.color
        )
    color_preview.short_description = 'Couleur'
    
    def projects_count(self, obj):
        return obj.project_set.count()
    projects_count.short_description = 'Nombre de projets'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'date_realisation', 'featured', 'views_count', 'likes_count', 'created_at']
    list_filter = ['category', 'status', 'featured', 'created_at', 'tags']
    search_fields = ['title', 'description', 'technologies']
    filter_horizontal = ['tags']
    readonly_fields = ['views_count', 'created_at', 'updated_at']

    def get_changeform_initial_data(self, request):
        # Valeurs proposées par défaut pour un nouveau projet
        initial = super().get_changeform_initial_data(request)
        initial.setdefault('user', request.user.pk)
        initial.setdefault('status', 'en_cours')
        initial.setdefault('technologies', 'Django, Python, JavaScript')
        return initial
    
    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'views_count', 'published_date']
    list_filter = ['is_published', 'published_date', 'tags']
    search_fields = ['title', 'content', 'excerpt']
    filter_horizontal = ['tags']
    readonly_fields = ['views_count', 'published_date', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}

    def get_changeform_initial_data(self, request):
        # Un nouvel article commence en brouillon
        initial = super().get_changeform_initial_data(request)
        initial.setdefault('is_published', False)
        return initial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'company', 'rating', 'is_featured', 'created_at']
    list_filter = ['rating', 'is_featured', 'created_at']
    search_fields = ['name', 'position', 'company', 'message']
    readonly_fields = ['created_at']

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['title', 'language', 'is_active', 'download_count', 'created_at']
    list_filter = ['language', 'is_active', 'created_at']
    readonly_fields = ['download_count', 'created_at']

@admin.register(ProjectLike)
class ProjectLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'project__title']

@admin.register(PortfolioStats)
class PortfolioStatsAdmin(admin.ModelAdmin):
    list_display = ['total_projects', 'total_blog_posts', 'total_views', 'total_likes', 'last_updated']
    readonly_fields = ['last_updated']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['email', 'message_preview']
    search_fields = ['email', 'message']
    readonly_fields = ['email', 'message']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'location', 'get_education_level']
    search_fields = ['user__username', 'full_name', 'location']
    list_filter = ['education_level', 'sex', 'civil_status', 'country']
    
    def get_education_level(self, obj):
        if obj.education_level:
            return obj.get_education_level_display()
        return '-'
    get_education_level.short_description = 'Niveau d\'études'

# ===== ADMIN GOOGLE ADSENSE =====

@admin.register(AdSenseConfig)
class AdSenseConfigAdmin(admin.ModelAdmin):
    list_display = ['publisher_id', 'is_active', 'test_mode', 'updated_at']
    list_filter = ['is_active', 'test_mode']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        # Permettre seulement une configuration
        return not AdSenseConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Ne pas permettre la suppression de la configuration
        return False

@admin.register(AdUnit)
class AdUnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'ad_type', 'ad_size', 'is_active', 'device_display', 'created_at']
    list_filter = ['position', 'ad_type', 'ad_size', 'is_active', 'show_on_mobile', 'show_on_desktop']
    search_fields = ['name', 'ad_unit_id', 'pages_to_show', 'pages_to_exclude']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'ad_unit_id', 'ad_type', 'is_active')
        }),
        ('Configuration de taille', {
            'fields': ('ad_size', 'custom_width', 'custom_height'),
            'description': 'Utilisez les champs personnalisés seulement si vous sélectionnez "Custom Size"'
        }),
        ('Positionnement', {
            'fields': ('position',)
        }),
        ('Ciblage d\'appareil', {
            'fields': ('show_on_mobile', 'show_on_desktop')
        }),
        ('Ciblage de pages', {
            'fields': ('pages_to_show', 'pages_to_exclude'),
            'description': 'Laissez vide pour afficher sur toutes les pages'
        }),
        ('Personnalisation', {
            'fields': ('custom_css',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def device_display(self, obj):
        devices = []
        if obj.show_on_mobile:
            devices.append('📱 Mobile')
        if obj.show_on_desktop:
            devices.append('💻 Desktop')
        return ' | '.join(devices) if devices else '❌ Aucun'
    device_display.short_description = 'Appareils'

@admin.register(AdPerformance)
class AdPerformanceAdmin(admin.ModelAdmin):
    list_display = ['ad_unit', 'date', 'impressions', 'clicks', 'ctr_display', 'revenue']
    list_filter = ['date', 'ad_unit']
    search_fields = ['ad_unit__name']
    readonly_fields = ['created_at', 'ctr_display']
    date_hierarchy = 'date'
    
    def ctr_display(self, obj):
        return f"{obj.ctr:.2f}%"
    ctr_display.short_description = 'CTR'
    
    def save_model(self, request, obj, form, change):
        # Calculer automatiquement le CTR
        obj.calculate_ctr()
        super().save_model(request, obj, form, change)

# Enregistrement des autres modèles avec configuration de base
admin.site.register(Skill)
admin.site.register(Category)
admin.site.register(About)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(Notification)



# ===== GALERIE =====

@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ['thumbnail', 'title', 'album', 'taken_at', 'is_published', 'is_featured', 'order']
    list_display_links = ['thumbnail', 'title']
    list_editable = ['is_published', 'is_featured', 'order']
    list_filter = ['is_published', 'is_featured', 'album']
    search_fields = ['title', 'alt_text', 'description', 'keywords', 'album', 'location']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['preview', 'width', 'height', 'created_at', 'updated_at']

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial.setdefault('location', 'Kinshasa, RDC')
        return initial
    fieldsets = (
        ('Photo', {'fields': ('image', 'preview', 'title', 'alt_text')}),
        ('Référencement (Google et IA)', {
            'fields': ('description', 'keywords', 'album', 'location', 'taken_at', 'slug'),
            'description': "Ces informations apparaissent sur la page de la photo et sont lues par Google, Google Images et les assistants IA.",
        }),
        ('Affichage', {'fields': ('is_published', 'is_featured', 'order')}),
        ('Informations', {'fields': ('width', 'height', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" alt="" style="width:64px;height:64px;object-fit:cover;border-radius:6px">', obj.image.url)
        return '-'
    thumbnail.short_description = 'Aperçu'

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" alt="" style="max-width:360px;border-radius:8px">', obj.image.url)
        return "L'aperçu apparaîtra après l'enregistrement."
    preview.short_description = 'Aperçu'


# ===== ACCUEIL : EN-TÊTE (fiche unique) =====

@admin.register(HomeHero)
class HomeHeroAdmin(admin.ModelAdmin):
    readonly_fields = ['photo_preview', 'updated_at']
    fieldsets = (
        ('Texte', {'fields': ('name', 'role', 'intro')}),
        ('Photo', {'fields': ('photo', 'photo_preview', 'photo_alt')}),
        ('Boutons', {'fields': ('primary_label', 'primary_url', 'secondary_label', 'secondary_url')}),
        ('Informations sous les boutons', {'fields': ('technologies', 'show_projects_count', 'show_cv')}),
        ('Suivi', {'fields': ('updated_at',), 'classes': ('collapse',)}),
    )

    def photo_preview(self, obj):
        from django.templatetags.static import static
        url = obj.photo.url if obj and obj.photo else static('images/profil1.jpg')
        return format_html('<img src="{}" alt="" style="width:160px;height:160px;object-fit:cover;border-radius:50%">', url)
    photo_preview.short_description = 'Aperçu'

    # Une seule fiche : on ouvre directement le formulaire de modification
    def has_add_permission(self, request):
        return not HomeHero.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect
        from django.urls import reverse
        obj = HomeHero.get_solo()
        return redirect(reverse('admin:portfolioapp_homehero_change', args=[obj.pk]))
