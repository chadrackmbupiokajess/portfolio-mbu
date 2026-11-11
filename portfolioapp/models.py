from django.db import models
from django.contrib.auth.models import User
#from ckeditor.fields import RichTextField
from django_ckeditor_5.fields import CKEditor5Field
from django.urls import reverse
from django_countries.fields import CountryField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

# Modèle Category
class Category(models.Model):
    name = models.CharField(max_length=120)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.name

# Modèle Tag
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#007bff', help_text="Couleur hexadécimale")

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name

# Modèle Project
class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="Chadrack Mbu Jess")
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Tags")
    description = CKEditor5Field()
    image = models.ImageField(upload_to='projects/', null=True, blank=True)
    project_url = models.URLField(blank=True, null=True, verbose_name="URL du projet")
    github_url = models.URLField(blank=True, null=True, verbose_name="URL GitHub")
    demo_url = models.URLField(blank=True, null=True, verbose_name="URL de démonstration")
    technologies = models.CharField(max_length=500, blank=True, help_text="Technologies utilisées (séparées par des virgules)")
    status = models.CharField(max_length=20, choices=[
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('pause', 'En pause'),
        ('archive', 'Archivé')
    ], default='termine')
    featured = models.BooleanField(default=False, verbose_name="Projet mis en avant")
    date_realisation = models.DateField(
        null=True, blank=True, verbose_name="Date de réalisation",
        help_text="Mois de fin du projet (ou de début s'il est en cours). Seuls le mois et l'année sont affichés. "
                  "Laissez vide pour utiliser la date d'ajout sur le site."
    )
    views_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de vues")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])

    @property
    def display_date(self):
        """Date affichée sur le site : date de réalisation, sinon date d'ajout."""
        return self.date_realisation or self.created_at.date()
from django.db.models.signals import post_save
from django.dispatch import receiver

class Comment(models.Model):
    project = models.ForeignKey(Project, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    image = models.ImageField(upload_to='comment_images/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'

    def __str__(self):
        return f"Comment by {self.author.username} on {self.project.title}"

    def like_count(self):
        return self.likes.count()

    def reply_count(self):
        return self.replies.count()

    def get_replies(self):
        return self.replies.filter(is_deleted=False).order_by('created_at')

    def get_absolute_url(self):
        return f"{self.project.get_absolute_url()}#comment-{self.id}"

class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_replies', blank=True)
    image = models.ImageField(upload_to='reply_images/', blank=True, null=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Réponse'
        verbose_name_plural = 'Réponses'
        ordering = ['created_at']

    def __str__(self):
        return f"Reply by {self.author.username} to {self.comment.author.username}"


# Modèle Notification
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

    def mark_as_read(self):
        """Marque la notification comme lue."""
        if not self.is_read:
            self.is_read = True
            self.save()

# Modèle Profile
class Profile(models.Model):
    SEX_CHOICES = [('M', 'Masculin'), ('F', 'Féminin'), ('O', 'Autre')]
    CIVIL_STATUS_CHOICES = [('S', 'Célibataire'), ('M', 'Marié(e)'), ('D', 'Divorcé(e)'), ('W', 'Veuf/Veuve')]
    EDUCATION_LEVEL_CHOICES = [('P', 'Primaire'), ('S', 'Secondaire'), ('B', 'Baccalauréat'), ('L', 'Licence'), ('M', 'Master'), ('D', 'Doctorat')]

    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, verbose_name="Photo de profil")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nom complet")
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=True, null=True, verbose_name="Sexe")
    bio = models.TextField(blank=True, null=True, verbose_name="Bio")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Date de naissance")
    civil_status = models.CharField(max_length=1, choices=CIVIL_STATUS_CHOICES, blank=True, null=True, verbose_name="État civil")
    activities = models.TextField(blank=True, null=True, verbose_name="Activités")
    education_level = models.CharField(max_length=1, choices=EDUCATION_LEVEL_CHOICES, blank=True, null=True, verbose_name="Niveau d'études")
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name="Localisation")
    country = CountryField(blank=True, null=True, verbose_name="Pays", default='FR')
    city = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ville")

    def __str__(self):
        return f"Profil de {self.user.username}"

# Signaux pour créer/sauvegarder un profil automatiquement
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # S'assurer que l'utilisateur a un profil, sinon le créer SEULEMENT s'il n'existe pas
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

# Modèle Skill
class Skill(models.Model):
    title = models.CharField(max_length=100)
    level = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Compétence"
        verbose_name_plural = "Compétences"

    def __str__(self):
        return self.title

# Modèle Contact
class Contact(models.Model):
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.email

# Modèle About
class About(models.Model):
    description = CKEditor5Field(verbose_name="Description")
    photo = models.ImageField(upload_to='about/', verbose_name="Photo de profil")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    def __str__(self):
        return "À propos de moi"

    class Meta:
        verbose_name = "À propos"
        verbose_name_plural = "À propos"

# Modèle Like pour les projets
class ProjectLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')
        verbose_name = "Like de projet"
        verbose_name_plural = "Likes de projets"

    def __str__(self):
        return f"{self.user.username} likes {self.project.title}"

# Modèle Testimonial
class Testimonial(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    position = models.CharField(max_length=100, verbose_name="Poste")
    company = models.CharField(max_length=100, blank=True, verbose_name="Entreprise")
    message = models.TextField(verbose_name="Témoignage")
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True, verbose_name="Photo")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5, verbose_name="Note")
    is_featured = models.BooleanField(default=False, verbose_name="Mis en avant")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Témoignage"
        verbose_name_plural = "Témoignages"
        ordering = ['-created_at']

    def __str__(self):
        return f"Témoignage de {self.name}"

# Modèle CV
class Resume(models.Model):
    title = models.CharField(max_length=100, verbose_name="Titre du CV")
    file = models.FileField(upload_to='resumes/', verbose_name="Fichier CV")
    language = models.CharField(max_length=10, choices=[
        ('fr', 'Français'),
        ('en', 'English')
    ], default='fr', verbose_name="Langue")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    download_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de téléchargements")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "CV"
        verbose_name_plural = "CVs"

    def __str__(self):
        return self.title

    def increment_downloads(self):
        self.download_count += 1
        self.save(update_fields=['download_count'])

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = CKEditor5Field()
    excerpt = models.TextField(max_length=300, blank=True, help_text="Résumé de l'article")
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Tags")
    is_published = models.BooleanField(default=True, verbose_name="Publié")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de vues")
    published_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = ("Article de blog")
        verbose_name_plural = ("Articles de blog")
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])

# Modèle pour les statistiques du portfolio
class PortfolioStats(models.Model):
    total_projects = models.PositiveIntegerField(default=0)
    total_blog_posts = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    total_likes = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Statistiques du portfolio"
        verbose_name_plural = "Statistiques du portfolio"

    def __str__(self):
        return f"Stats - {self.last_updated.strftime('%d/%m/%Y')}"

# ===== SIGNAUX =====
# Tous les signaux sont définis ici après la déclaration de tous les modèles

# Signal pour créer une notification lorsqu'un commentaire est ajouté
@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created:
        # Récupérer tous les utilisateurs qui ont participé à ce projet
        participants = set()

        # Ajouter le propriétaire du projet
        participants.add(instance.project.user)

        # Ajouter tous les utilisateurs qui ont commenté ce projet
        for comment in Comment.objects.filter(project=instance.project):
            participants.add(comment.author)

        # Ajouter tous les utilisateurs qui ont répondu aux commentaires de ce projet
        for comment in Comment.objects.filter(project=instance.project):
            for reply in Reply.objects.filter(comment=comment):
                participants.add(reply.author)

        # Supprimer l'auteur du nouveau commentaire de la liste
        participants.discard(instance.author)

        # Créer une notification pour chaque participant
        for user in participants:
            if instance.project.user == user:
                # Message spécial pour le propriétaire du projet
                message = f"{instance.author.username} a commenté votre projet : {instance.project.title}"
            else:
                # Message pour les autres participants
                message = f"{instance.author.username} a ajouté un commentaire sur le projet : {instance.project.title}"

            Notification.objects.create(
                user=user,
                message=message,
                link=f"/projects/{instance.project.id}/"
            )

# Signal pour créer une notification lorsqu'une réponse est ajoutée
@receiver(post_save, sender=Reply)
def create_reply_notification(sender, instance, created, **kwargs):
    if created:
        # Récupérer tous les utilisateurs qui ont participé à ce projet
        participants = set()

        # Ajouter le propriétaire du projet
        participants.add(instance.comment.project.user)

        # Ajouter l'auteur du commentaire original
        participants.add(instance.comment.author)

        # Ajouter tous les utilisateurs qui ont commenté ce projet
        for comment in Comment.objects.filter(project=instance.comment.project):
            participants.add(comment.author)

        # Ajouter tous les utilisateurs qui ont répondu aux commentaires de ce projet
        for comment in Comment.objects.filter(project=instance.comment.project):
            for reply in Reply.objects.filter(comment=comment):
                participants.add(reply.author)

        # Supprimer l'auteur de la nouvelle réponse de la liste
        participants.discard(instance.author)

        # Créer une notification pour chaque participant
        for user in participants:
            if user == instance.comment.author:
                # Message spécial pour l'auteur du commentaire original
                message = f"{instance.author.username} a répondu à votre commentaire sur le projet : {instance.comment.project.title}"
            elif user == instance.comment.project.user:
                # Message pour le propriétaire du projet
                message = f"{instance.author.username} a répondu à un commentaire sur votre projet : {instance.comment.project.title}"
            else:
                # Message pour les autres participants
                message = f"{instance.author.username} a ajouté une réponse sur le projet : {instance.comment.project.title}"

            Notification.objects.create(
                user=user,
                message=message,
                link=f"/projects/{instance.comment.project.id}/"
            )

# Signal pour générer automatiquement le slug des articles de blog
@receiver(post_save, sender=BlogPost)
def generate_blog_slug(sender, instance, created, **kwargs):
    if created and not instance.slug:
        base_slug = slugify(instance.title)
        slug = base_slug
        counter = 1
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        instance.slug = slug
        instance.save(update_fields=['slug'])

# Signal pour créer une notification lors d'un like
@receiver(post_save, sender=ProjectLike)
def create_like_notification(sender, instance, created, **kwargs):
    if created and instance.project.user != instance.user:
        Notification.objects.create(
            user=instance.project.user,
            message=f"{instance.user.username} a aimé votre projet : {instance.project.title}",
            link=f"/projects/{instance.project.id}/"
        )

# ===== MODÈLES GOOGLE ADSENSE =====

class AdSenseConfig(models.Model):
    """Configuration globale pour Google AdSense"""
    publisher_id = models.CharField(
        max_length=50,
        verbose_name="Publisher ID",
        help_text="Votre ID éditeur Google AdSense (ca-pub-xxxxxxxxxx)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activer AdSense",
        help_text="Activer/désactiver l'affichage des publicités"
    )
    test_mode = models.BooleanField(
        default=False,
        verbose_name="Mode test",
        help_text="Activer le mode test pour les annonces"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuration AdSense"
        verbose_name_plural = "Configurations AdSense"

    def __str__(self):
        return f"AdSense Config - {self.publisher_id}"

    @classmethod
    def get_config(cls):
        """Récupère la configuration AdSense active"""
        config, created = cls.objects.get_or_create(
            id=1,
            defaults={
                'publisher_id': 'ca-pub-0000000000000000',
                'is_active': False,
                'test_mode': True
            }
        )
        return config

class AdUnit(models.Model):
    """Unité publicitaire AdSense"""
    AD_TYPES = [
        ('display', 'Display'),
        ('in_article', 'In-Article'),
        ('in_feed', 'In-Feed'),
        ('matched_content', 'Matched Content'),
        ('auto', 'Auto Ads'),
    ]

    AD_SIZES = [
        ('responsive', 'Responsive'),
        ('728x90', 'Leaderboard (728x90)'),
        ('300x250', 'Medium Rectangle (300x250)'),
        ('320x50', 'Mobile Banner (320x50)'),
        ('160x600', 'Wide Skyscraper (160x600)'),
        ('300x600', 'Half Page (300x600)'),
        ('970x250', 'Billboard (970x250)'),
        ('custom', 'Custom Size'),
    ]

    POSITIONS = [
        ('header', 'Header'),
        ('sidebar', 'Sidebar'),
        ('content_top', 'Top of Content'),
        ('content_middle', 'Middle of Content'),
        ('content_bottom', 'Bottom of Content'),
        ('footer', 'Footer'),
        ('between_posts', 'Between Posts'),
        ('popup', 'Popup'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="Nom de l'unité",
        help_text="Nom descriptif pour identifier l'unité publicitaire"
    )
    ad_unit_id = models.CharField(
        max_length=50,
        verbose_name="ID de l'unité publicitaire",
        help_text="ID de l'unité publicitaire Google AdSense"
    )
    ad_type = models.CharField(
        max_length=20,
        choices=AD_TYPES,
        default='display',
        verbose_name="Type d'annonce"
    )
    ad_size = models.CharField(
        max_length=20,
        choices=AD_SIZES,
        default='responsive',
        verbose_name="Taille de l'annonce"
    )
    custom_width = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Largeur personnalisée",
        help_text="Largeur en pixels (pour taille personnalisée)"
    )
    custom_height = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Hauteur personnalisée",
        help_text="Hauteur en pixels (pour taille personnalisée)"
    )
    position = models.CharField(
        max_length=20,
        choices=POSITIONS,
        verbose_name="Position"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    show_on_mobile = models.BooleanField(
        default=True,
        verbose_name="Afficher sur mobile"
    )
    show_on_desktop = models.BooleanField(
        default=True,
        verbose_name="Afficher sur desktop"
    )
    pages_to_show = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Pages à afficher",
        help_text="URLs des pages où afficher cette annonce (séparées par des virgules). Laisser vide pour toutes les pages."
    )
    pages_to_exclude = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Pages à exclure",
        help_text="URLs des pages où ne pas afficher cette annonce (séparées par des virgules)"
    )
    custom_css = models.TextField(
        blank=True,
        verbose_name="CSS personnalisé",
        help_text="CSS personnalisé pour styliser l'unité publicitaire"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Unité publicitaire"
        verbose_name_plural = "Unités publicitaires"
        ordering = ['position', 'name']

    def __str__(self):
        return f"{self.name} ({self.position})"

    def should_display_on_page(self, current_path):
        """Vérifie si l'annonce doit être affichée sur la page actuelle"""
        if not self.is_active:
            return False

        # Vérifier les pages à exclure
        if self.pages_to_exclude:
            excluded_pages = [page.strip() for page in self.pages_to_exclude.split(',')]
            if any(excluded_page in current_path for excluded_page in excluded_pages):
                return False

        # Vérifier les pages à inclure
        if self.pages_to_show:
            included_pages = [page.strip() for page in self.pages_to_show.split(',')]
            return any(included_page in current_path for included_page in included_pages)

        return True

    def get_ad_code(self):
        """Génère le code HTML de l'annonce AdSense"""
        config = AdSenseConfig.get_config()

        if not config.is_active:
            return ""

        # Déterminer la taille
        if self.ad_size == 'responsive':
            size_style = 'display:block; width:100%; height:auto;'
            size_attrs = 'data-ad-format="auto" data-full-width-responsive="true"'
        elif self.ad_size == 'custom' and self.custom_width and self.custom_height:
            size_style = f'display:inline-block; width:{self.custom_width}px; height:{self.custom_height}px;'
            size_attrs = f'data-ad-format="rectangle"'
        else:
            width, height = self.ad_size.split('x') if 'x' in self.ad_size else ('300', '250')
            size_style = f'display:inline-block; width:{width}px; height:{height}px;'
            size_attrs = f'data-ad-format="rectangle"'

        # Mode test
        test_attr = 'data-adtest="on"' if config.test_mode else ''

        ad_code = f'''
        <div class="adsense-unit" data-position="{self.position}">
            <ins class="adsbygoogle"
                 style="{size_style}"
                 data-ad-client="{config.publisher_id}"
                 data-ad-slot="{self.ad_unit_id}"
                 {size_attrs}
                 {test_attr}>
            </ins>
            <script>
                (adsbygoogle = window.adsbygoogle || []).push({{}});
            </script>
        </div>
        '''

        return ad_code.strip()

class AdPerformance(models.Model):
    """Suivi des performances des annonces"""
    ad_unit = models.ForeignKey(
        AdUnit,
        on_delete=models.CASCADE,
        related_name='performances',
        verbose_name="Unité publicitaire"
    )
    date = models.DateField(verbose_name="Date")
    impressions = models.PositiveIntegerField(
        default=0,
        verbose_name="Impressions"
    )
    clicks = models.PositiveIntegerField(
        default=0,
        verbose_name="Clics"
    )
    ctr = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="CTR (%)",
        help_text="Click-through rate en pourcentage"
    )
    revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Revenus ($)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Performance publicitaire"
        verbose_name_plural = "Performances publicitaires"
        unique_together = ['ad_unit', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.ad_unit.name} - {self.date}"

    def calculate_ctr(self):
        """Calcule le CTR automatiquement"""
        if self.impressions > 0:
            self.ctr = (self.clicks / self.impressions) * 100
        else:
            self.ctr = 0.00

# ===== GALERIE PHOTOS =====

class GalleryPhoto(models.Model):
    """Photo publiée dans la galerie. Chaque photo a sa propre page,
    lisible par Google, les moteurs d'images et les assistants IA."""
    title = models.CharField("Titre", max_length=150)
    slug = models.SlugField(
        "Adresse de la page", max_length=170, unique=True, blank=True,
        help_text="Laissez vide : elle est créée automatiquement à partir du titre."
    )
    image = models.ImageField(
        "Image", upload_to='galerie/%Y/',
        width_field='width', height_field='height',
        help_text="JPG ou WebP de préférence, 2000 px de large maximum."
    )
    width = models.PositiveIntegerField("Largeur (px)", null=True, blank=True, editable=False)
    height = models.PositiveIntegerField("Hauteur (px)", null=True, blank=True, editable=False)
    alt_text = models.CharField(
        "Ce que montre l'image", max_length=200,
        help_text="Une phrase précise, lue par Google, les IA et les lecteurs d'écran. "
                  "Exemple : « Chadrack Mbu Jess présente Jessna CinéHub sur une TV connectée »."
    )
    description = models.TextField(
        "Texte de la page", blank=True,
        help_text="Contexte de la photo : où, quand, pourquoi. Plus c'est précis, mieux c'est référencé."
    )
    album = models.CharField("Album", max_length=80, blank=True, help_text="Exemple : Événements, Projets, Portraits, Design.")
    location = models.CharField("Lieu", max_length=120, blank=True, help_text="Exemple : Kinshasa, RDC.")
    taken_at = models.DateField("Date de la photo", null=True, blank=True)
    keywords = models.CharField("Mots-clés", max_length=255, blank=True, help_text="Séparés par des virgules.")
    is_published = models.BooleanField("Publiée", default=True)
    is_featured = models.BooleanField("Afficher sur l'accueil", default=False)
    order = models.PositiveIntegerField("Ordre", default=0, help_text="Plus le nombre est petit, plus la photo apparaît tôt.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Photo de la galerie"
        verbose_name_plural = "Galerie photos"
        ordering = ['order', '-taken_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:150] or 'photo'
            slug, n = base, 2
            while GalleryPhoto.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('gallery_detail', args=[self.slug])

    @property
    def keyword_list(self):
        return [k.strip() for k in self.keywords.split(',') if k.strip()]


# ===== ACCUEIL (en-tête de la page d'accueil, modifiable dans l'administration) =====

DEFAULT_HERO_TEXT = (
    "Je conçois et développe des applications web sur mesure, du site vitrine à la plateforme complète : "
    "une base de code soignée, des interfaces claires et un produit qui tient la route une fois en ligne."
)


class HomeHero(models.Model):
    """En-tête de la page d'accueil. Une seule fiche existe : on la modifie, on ne la recrée pas."""
    name = models.CharField("Nom affiché", max_length=80, default="Chadrack Mbu Jess")
    role = models.CharField("Métier", max_length=120, default="Développeur full-stack",
                            help_text="Affiché en doré sous le nom. Exemple : Développeur full-stack et designer.")
    intro = models.TextField("Texte de présentation", default=DEFAULT_HERO_TEXT,
                             help_text="2 ou 3 phrases maximum : ce que vous faites et pour qui.")
    photo = models.ImageField("Photo", upload_to='accueil/', blank=True,
                              help_text="Photo carrée de préférence (au moins 800 × 800 px). "
                                        "Laissez vide pour garder la photo actuelle.")
    photo_alt = models.CharField("Description de la photo", max_length=150, default="Portrait de Chadrack Mbu Jess",
                                 help_text="Lue par Google et les lecteurs d'écran.")
    primary_label = models.CharField("Bouton principal : texte", max_length=40, default="Voir mes projets")
    primary_url = models.CharField("Bouton principal : lien", max_length=200, blank=True,
                                   help_text="Laissez vide pour la page Projets. Exemple : /galerie/ ou https://…")
    secondary_label = models.CharField("Bouton secondaire : texte", max_length=40, default="Me contacter", blank=True,
                                       help_text="Laissez vide pour masquer ce bouton.")
    secondary_url = models.CharField("Bouton secondaire : lien", max_length=200, blank=True,
                                     help_text="Laissez vide pour la page Contact.")
    technologies = models.CharField("Technologies", max_length=150, default="Python, Django, JavaScript", blank=True,
                                    help_text="Ligne affichée sous les boutons. Laissez vide pour la masquer.")
    show_projects_count = models.BooleanField("Afficher le nombre de projets", default=True)
    show_cv = models.BooleanField("Afficher le lien vers le CV", default=True,
                                  help_text="Nécessite un CV ajouté dans la rubrique CV.")
    updated_at = models.DateTimeField("Dernière modification", auto_now=True)

    class Meta:
        verbose_name = "Accueil : en-tête"
        verbose_name_plural = "Accueil : en-tête"

    def __str__(self):
        return "En-tête de la page d'accueil"

    def save(self, *args, **kwargs):
        self.pk = 1  # une seule fiche
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
