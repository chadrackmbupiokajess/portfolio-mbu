"""
Remplit l'administration avec des exemples prêts à modifier.

    python manage.py remplir_exemples

- Ne crée rien en double : un élément qui existe déjà (même nom ou même titre) est laissé tel quel.
- Les 3 articles de blog sont complets et publiés directement.
- Aucun témoignage n'est inventé : un témoignage doit venir d'un vrai client.
"""
import io
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from ._articles import ARTICLES, OLD_DRAFT_SLUGS
from portfolioapp.models import (
    About, BlogPost, Category, GalleryPhoto, Project, Skill, Tag,
)

BASE = Path(settings.BASE_DIR)


def image_file(relative_path, max_width=2000):
    """Lit une image du projet et la réduit (2000 px de large max) pour la galerie."""
    path = BASE / relative_path
    if not path.exists():
        return None
    try:
        from PIL import Image
        img = Image.open(path)
        img = img.convert('RGB')
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, round(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, 'JPEG', quality=85, optimize=True, progressive=True)
        return ContentFile(buf.getvalue())
    except Exception:
        return ContentFile(path.read_bytes())


class Command(BaseCommand):
    help = "Ajoute 3 exemples par rubrique (catégories, mots-clés, projets, articles, galerie, compétences, à propos)."

    def handle(self, *args, **options):
        created = []

        # ---------- Utilisateur propriétaire des projets ----------
        User = get_user_model()
        owner = User.objects.filter(is_superuser=True).order_by('id').first() or User.objects.order_by('id').first()
        if not owner:
            self.stderr.write(self.style.ERROR(
                "Aucun utilisateur trouvé. Créez d'abord un administrateur : python manage.py createsuperuser"))
            return

        # ---------- Catégories ----------
        cats = {}
        for name in ['App Web', 'Streaming', 'Design']:
            cats[name], new = Category.objects.get_or_create(name=name)
            if new:
                created.append(f"Catégorie : {name}")

        # ---------- Mots-clés ----------
        tags = {}
        for name, color in [('Django', '#0c4b33'), ('Python', '#3776ab'), ('JavaScript', '#c9a400')]:
            tags[name], new = Tag.objects.get_or_create(name=name, defaults={'color': color})
            if new:
                created.append(f"Mot-clé : {name}")

        # ---------- Projets ----------
        projects = [
            {
                'title': 'Jessna CinéHub',
                'category': cats['Streaming'],
                'status': 'en_cours',
                'featured': True,
                'technologies': 'Application mobile, Application PC, Application TV',
                'tags': [],
                'description': (
                    "<p><strong>Jessna CinéHub</strong> est une plateforme de streaming de films, de séries et d'animés, "
                    "disponible sur mobile, sur ordinateur et sur TV.</p>"
                    "<h2>L'objectif</h2>"
                    "<p>Offrir un catalogue riche et une expérience de visionnage simple, sur l'écran que l'on a sous la main : "
                    "le téléphone dans les transports, l'ordinateur au bureau, la TV à la maison.</p>"
                    "<h2>Ce que propose la plateforme</h2>"
                    "<ul><li>Films, séries et animés au même endroit</li>"
                    "<li>Une application pour mobile, PC et TV</li>"
                    "<li>Une identité visuelle forte, reconnaissable à son logo JnC</li></ul>"
                    "<p>Ajoutez ici les fonctionnalités, les chiffres et le lien de téléchargement.</p>"
                ),
            },
            {
                'title': "Jessna Event : invitations de mariage à QR code",
                'category': cats['App Web'],
                'status': 'en_cours',
                'featured': True,
                'technologies': 'Django, Django Channels (WebSocket), Next.js',
                'tags': ['Django', 'Python', 'JavaScript'],
                'description': (
                    "<p>Une application web qui gère les invitations de mariage du début à la fin, avec un "
                    "<strong>QR code unique par invité</strong>.</p>"
                    "<h2>Comment ça marche</h2>"
                    "<ul><li>L'administrateur crée le mariage et le compte des mariés.</li>"
                    "<li>Les mariés ajoutent leurs invités depuis leur espace.</li>"
                    "<li>Chaque invitation est générée avec un QR code ; tout son contenu (textes, polices, image de fond) se règle depuis l'administration.</li>"
                    "<li>À l'entrée, l'agent de sécurité scanne le QR code : la table de l'invité s'affiche et sa présence est enregistrée en temps réel.</li></ul>"
                    "<h2>Choix techniques</h2>"
                    "<p>Back-end Django avec WebSocket pour les mises à jour en direct, front-end Next.js pour une interface rapide, sans rechargement de page.</p>"
                ),
            },
            {
                'title': 'BisoFood',
                'category': cats['App Web'],
                'status': 'en_cours',
                'featured': False,
                'technologies': 'Application, Identité visuelle',
                'tags': [],
                'description': (
                    "<p><strong>BisoFood</strong> est une marque et une application que j'ai créées, de l'idée jusqu'à l'identité visuelle.</p>"
                    "<h2>L'identité visuelle</h2>"
                    "<p>Le logo associe une flamme et un « b » souriant, dans une palette orange chaleureuse : "
                    "une marque facile à reconnaître et accueillante.</p>"
                    "<p>Ajoutez ici les fonctionnalités de l'application et des captures d'écran.</p>"
                ),
            },
        ]
        for data in projects:
            tag_names = data.pop('tags')
            project, new = Project.objects.get_or_create(
                title=data['title'], defaults={**data, 'user': owner})
            if new:
                project.tags.set([tags[t] for t in tag_names])
                created.append(f"Projet : {project.title}")

        # ---------- Articles de blog (complets et publiés) ----------
        # Remplace les plans « À compléter » d'une version précédente, s'ils n'ont pas été modifiés
        for old_slug in OLD_DRAFT_SLUGS:
            old = BlogPost.objects.filter(slug=old_slug).first()
            if old and 'À compléter' in (old.content or '') and old_slug not in [a['slug'] for a in ARTICLES]:
                old.delete()
                created.append(f"Plan d'article remplacé : {old.title}")
        for article in ARTICLES:
            data = {k: v for k, v in article.items() if k not in ('tags', 'slug')}
            post = BlogPost.objects.filter(slug=article['slug']).first()
            if post and 'À compléter' not in (post.content or ''):
                continue  # article déjà écrit ou modifié : on n'y touche pas
            if post:
                for key, value in data.items():
                    setattr(post, key, value)
                post.is_published = True
                post.save()
            else:
                post = BlogPost.objects.create(slug=article['slug'], is_published=True, **data)
            post.tags.set([tags[t] for t in article['tags']])
            created.append(f"Article publié : {post.title}")

        # ---------- Galerie ----------
        photos = [
            {
                'file': 'static/images/mbu.jpg',
                'title': 'Présentation au micro',
                'alt_text': "Chadrack Mbu Jess, en costume, prend la parole au micro devant un écran d'ordinateur",
                'description': "Ajoutez ici le contexte : l'événement, le lieu, la date et le sujet présenté.",
                'album': 'Événements',
                'keywords': 'Chadrack Mbu Jess, présentation, informatique',
                'is_featured': True,
                'order': 1,
            },
            {
                'file': 'static/images/a.jpg',
                'title': 'Portrait officiel',
                'alt_text': "Portrait de Chadrack Mbu Jess en veste bleu marine, sur fond blanc",
                'description': "Portrait officiel de Chadrack Mbu Jess, développeur full-stack.",
                'album': 'Portraits',
                'keywords': 'Chadrack Mbu Jess, portrait, développeur full-stack',
                'is_featured': True,
                'order': 2,
            },
            {
                'file': 'media/about/profil.jpg',
                'title': 'En extérieur',
                'alt_text': "Chadrack Mbu Jess en chemise à carreaux et casquette, debout en extérieur",
                'description': "Ajoutez ici le contexte de la photo.",
                'album': 'Portraits',
                'keywords': 'Chadrack Mbu Jess, portrait',
                'is_featured': True,
                'order': 3,
            },
        ]
        for data in photos:
            if GalleryPhoto.objects.filter(title=data['title']).exists():
                continue
            content = image_file(data.pop('file'))
            if content is None:
                self.stdout.write(self.style.WARNING(f"Image introuvable pour « {data['title']} », photo ignorée."))
                continue
            photo = GalleryPhoto(**data)
            photo.image.save(f"{slugify(data['title'])}.jpg", content, save=False)
            photo.save()
            created.append(f"Photo : {photo.title}")

        # ---------- Compétences ----------
        for title, level in [
            ('Python et Django', 'Avancé'),
            ('JavaScript et Next.js', 'Intermédiaire'),
            ('Design graphique (Photoshop)', 'Avancé'),
        ]:
            _, new = Skill.objects.get_or_create(title=title, defaults={'level': level})
            if new:
                created.append(f"Compétence : {title}")

        # ---------- À propos ----------
        if not About.objects.exists():
            about = About(description=(
                "<p>Je suis <strong>Chadrack Mbu Jess</strong>, développeur full-stack. "
                "Je conçois et développe des applications web et desktop, des plateformes de diffusion de contenu "
                "comme Jessna CinéHub, ainsi que les identités visuelles qui les accompagnent.</p>"
                "<p>J'aime prendre un projet de l'idée jusqu'à la mise en ligne : comprendre le besoin, "
                "choisir les bons outils, construire une interface claire et un code solide.</p>"
            ))
            about.photo.name = 'about/profil.jpg'
            about.save()
            created.append("Page À propos")

        # ---------- Résumé ----------
        if created:
            self.stdout.write(self.style.SUCCESS(f"{len(created)} élément(s) ajouté(s) :"))
            for line in created:
                self.stdout.write(f"  + {line}")
        else:
            self.stdout.write(self.style.SUCCESS("Rien à ajouter : les exemples existent déjà."))
        self.stdout.write(
            "\nÀ faire ensuite dans l'administration :\n"
            "  - ajouter les images des projets et compléter leurs textes ;\n"
            "  - relire les 3 articles du blog (déjà publiés) ;\n"
            "  - compléter le contexte des photos de la galerie.\n"
            "Témoignages : aucun exemple créé, ils doivent venir de vrais clients "
            "(envoyez-leur le lien /testimonials/)."
        )
