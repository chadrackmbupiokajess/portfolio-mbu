"""Articles d'exemple complets, utilisés par la commande remplir_exemples."""
from html import escape


def code(text, lang=''):
    cls = f' class="language-{lang}"' if lang else ''
    return f'<pre><code{cls}>{escape(text.strip())}</code></pre>'


ARTICLES = [
    # ------------------------------------------------------------------
    {
        'title': "Mettre en ligne un site Django sur PythonAnywhere",
        'slug': 'mettre-en-ligne-un-site-django-sur-pythonanywhere',
        'tags': ['Django', 'Python'],
        'excerpt': (
            "Code, environnement virtuel, fichier WSGI, fichiers statiques et médias : "
            "les étapes que je suis pour publier un projet Django sur PythonAnywhere sans mauvaise surprise."
        ),
        'content': (
            "<p>Mon portfolio tourne sur PythonAnywhere. L'hébergeur est simple à prendre en main, mais quelques réglages "
            "font la différence entre un site qui marche du premier coup et une après-midi passée sur une page d'erreur. "
            "Voici la méthode que j'applique à chaque mise en ligne.</p>"

            "<h2>1. Récupérer le code sur le serveur</h2>"
            "<p>Depuis une console Bash de PythonAnywhere, je clone le dépôt GitHub du projet :</p>"
            + code("git clone https://github.com/mon-compte/portfolio-mbu.git\ncd portfolio-mbu", 'bash') +

            "<h2>2. Créer l'environnement virtuel</h2>"
            "<p>Chaque projet a son propre environnement, avec la même version de Python que celle choisie dans l'onglet <em>Web</em> :</p>"
            + code("mkvirtualenv portfolio --python=python3.13\npip install -r requirements.txt", 'bash') +
            "<p>Si une dépendance échoue, c'est souvent qu'elle n'est pas fixée dans <code>requirements.txt</code>. "
            "Fixer les versions évite qu'une mise à jour casse le site du jour au lendemain.</p>"

            "<h2>3. Régler <code>settings.py</code> pour la production</h2>"
            "<ul>"
            "<li><code>DEBUG = False</code> : sinon, les erreurs affichent votre code et vos réglages à tout le monde.</li>"
            "<li><code>ALLOWED_HOSTS</code> doit contenir votre domaine, par exemple <code>monsite.pythonanywhere.com</code>.</li>"
            "<li>La <code>SECRET_KEY</code> ne doit pas être dans le dépôt : je la lis depuis une variable d'environnement.</li>"
            "</ul>"
            + code("import os\nSECRET_KEY = os.environ['DJANGO_SECRET_KEY']\nDEBUG = False\nALLOWED_HOSTS = ['monsite.pythonanywhere.com']", 'python') +

            "<h2>4. Configurer le fichier WSGI</h2>"
            "<p>Dans l'onglet <em>Web</em>, le lien vers le fichier WSGI ouvre un fichier à adapter. Il faut indiquer le dossier du projet et le module de réglages :</p>"
            + code(
                "import os, sys\n"
                "path = '/home/moncompte/portfolio-mbu'\n"
                "if path not in sys.path:\n"
                "    sys.path.append(path)\n"
                "os.environ['DJANGO_SETTINGS_MODULE'] = 'portfolio.settings'\n\n"
                "from django.core.wsgi import get_wsgi_application\n"
                "application = get_wsgi_application()", 'python') +

            "<h2>5. Fichiers statiques et médias</h2>"
            "<p>En production, Django ne sert plus lui-même le CSS, le JavaScript et les images envoyées. On regroupe les fichiers statiques :</p>"
            + code("python manage.py collectstatic", 'bash') +
            "<p>Puis, dans l'onglet <em>Web</em>, section <em>Static files</em>, j'ajoute deux correspondances :</p>"
            "<ul>"
            "<li><code>/static/</code> vers <code>/home/moncompte/portfolio-mbu/staticfiles</code></li>"
            "<li><code>/media/</code> vers <code>/home/moncompte/portfolio-mbu/media</code></li>"
            "</ul>"

            "<h2>6. Base de données et premier lancement</h2>"
            + code("python manage.py migrate\npython manage.py createsuperuser", 'bash') +
            "<p>Il reste à cliquer sur <em>Reload</em> dans l'onglet <em>Web</em>. Ce bouton est à utiliser après chaque modification du code : "
            "c'est l'oubli le plus fréquent quand « rien ne change » sur le site.</p>"

            "<h2>En cas d'erreur</h2>"
            "<p>Le premier réflexe est l'<em>error log</em>, accessible depuis l'onglet <em>Web</em>. Il indique presque toujours le fichier et la ligne en cause, "
            "bien plus vite que de chercher à l'aveugle.</p>"
        ),
    },
    # ------------------------------------------------------------------
    {
        'title': "Scanner une invitation par QR code avec Django et WebSocket",
        'slug': 'scanner-une-invitation-par-qr-code-avec-django',
        'tags': ['Django', 'Python', 'JavaScript'],
        'excerpt': (
            "Pour Jessna Event, chaque invité reçoit un QR code unique. Au scan, sa table s'affiche et la liste de présence "
            "se met à jour en direct. Voici le principe, du modèle Django jusqu'au WebSocket."
        ),
        'content': (
            "<p>Dans Jessna Event, mon application d'invitations de mariage, l'agent à l'entrée scanne le QR code de chaque invité. "
            "Il voit immédiatement le nom et la table de la personne, et les mariés voient la liste de présence se remplir en direct. "
            "Voici comment ces trois briques s'assemblent.</p>"

            "<h2>1. Un identifiant impossible à deviner</h2>"
            "<p>Le QR code ne doit pas contenir l'identifiant numérique de l'invité : n'importe qui pourrait essayer 1, 2, 3… "
            "Chaque invité reçoit donc un jeton aléatoire :</p>"
            + code(
                "import uuid\nfrom django.db import models\n\n"
                "class Invite(models.Model):\n"
                "    mariage = models.ForeignKey('Mariage', on_delete=models.CASCADE, related_name='invites')\n"
                "    nom = models.CharField(max_length=120)\n"
                "    table = models.CharField(max_length=30)\n"
                "    jeton = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)\n"
                "    present = models.BooleanField(default=False)\n"
                "    arrive_a = models.DateTimeField(null=True, blank=True)", 'python') +

            "<h2>2. Générer le QR code</h2>"
            "<p>La bibliothèque <code>qrcode</code> produit l'image à placer sur l'invitation. Le QR code contient simplement le jeton :</p>"
            + code(
                "import qrcode\nfrom io import BytesIO\n\n"
                "def qr_png(invite):\n"
                "    img = qrcode.make(str(invite.jeton))\n"
                "    buffer = BytesIO()\n"
                "    img.save(buffer, format='PNG')\n"
                "    return buffer.getvalue()", 'python') +

            "<h2>3. La vue de scan</h2>"
            "<p>Le téléphone de l'agent lit le QR code (avec une bibliothèque JavaScript comme <code>html5-qrcode</code>) "
            "puis envoie le jeton au serveur. La vue marque l'invité présent et renvoie sa table :</p>"
            + code(
                "from django.contrib.auth.decorators import login_required\n"
                "from django.http import JsonResponse\n"
                "from django.shortcuts import get_object_or_404\n"
                "from django.utils import timezone\n\n"
                "@login_required\n"
                "def scanner(request, jeton):\n"
                "    invite = get_object_or_404(Invite, jeton=jeton)\n"
                "    deja_present = invite.present\n"
                "    if not deja_present:\n"
                "        invite.present = True\n"
                "        invite.arrive_a = timezone.now()\n"
                "        invite.save(update_fields=['present', 'arrive_a'])\n"
                "        notifier_presence(invite)\n"
                "    return JsonResponse({\n"
                "        'nom': invite.nom,\n"
                "        'table': invite.table,\n"
                "        'deja_present': deja_present,\n"
                "    })", 'python') +
            "<p>Le champ <code>deja_present</code> est important : il permet d'alerter l'agent si une même invitation est présentée deux fois.</p>"

            "<h2>4. La liste de présence en temps réel</h2>"
            "<p>Avec Django Channels, chaque mariage a son « groupe ». Quand un invité arrive, le serveur prévient tous les écrans abonnés à ce groupe, sans qu'ils aient à recharger la page :</p>"
            + code(
                "from asgiref.sync import async_to_sync\n"
                "from channels.layers import get_channel_layer\n\n"
                "def notifier_presence(invite):\n"
                "    async_to_sync(get_channel_layer().group_send)(\n"
                "        f'mariage_{invite.mariage_id}',\n"
                "        {'type': 'invite.arrive', 'nom': invite.nom, 'table': invite.table},\n"
                "    )", 'python') +
            "<p>Côté navigateur, l'interface Next.js ouvre une connexion WebSocket et ajoute chaque arrivée à la liste dès qu'elle est reçue.</p>"

            "<h2>Ce qu'il faut retenir</h2>"
            "<ul>"
            "<li>Un jeton aléatoire dans le QR code, jamais un identifiant qui se suit.</li>"
            "<li>Une vue de scan réservée aux personnes connectées, qui signale les doubles passages.</li>"
            "<li>Un groupe WebSocket par événement pour que tous les écrans restent à jour.</li>"
            "</ul>"
        ),
    },
    # ------------------------------------------------------------------
    {
        'title': "Rendre un site Django visible par Google et les assistants IA",
        'slug': 'rendre-un-site-django-visible-par-google-et-les-ia',
        'tags': ['Django', 'Python'],
        'excerpt': (
            "Plan du site avec images, robots.txt, llms.txt, données structurées et textes alternatifs : "
            "ce que j'ai mis en place sur ce portfolio pour être bien compris par Google et par les IA."
        ),
        'content': (
            "<p>Un beau site ne sert à rien si personne ne le trouve. Voici ce que j'ai mis en place sur ce portfolio pour que "
            "Google, Google Images et les assistants comme ChatGPT, Claude ou Perplexity comprennent qui je suis et ce que je fais.</p>"

            "<h2>1. Un plan du site qui inclut les images</h2>"
            "<p>Le fichier <code>/sitemap.xml</code> liste toutes les pages publiques : projets, articles et photos de la galerie. "
            "Pour chaque page, j'ajoute aussi l'adresse de ses images, ce qui aide Google Images :</p>"
            + code(
                "<url>\n"
                "  <loc>https://monsite.com/galerie/portrait-officiel/</loc>\n"
                "  <image:image>\n"
                "    <image:loc>https://monsite.com/media/galerie/portrait-officiel.jpg</image:loc>\n"
                "  </image:image>\n"
                "</url>", 'xml') +
            "<p>Le plan est généré par une vue Django à chaque visite : un nouveau projet y apparaît sans rien faire.</p>"

            "<h2>2. Un robots.txt qui accueille les bons robots</h2>"
            "<p>Le fichier <code>/robots.txt</code> autorise explicitement les moteurs de recherche et les robots des assistants IA, "
            "bloque seulement les pages privées (administration, comptes) et indique où trouver le plan du site.</p>"
            + code(
                "User-agent: Googlebot\nUser-agent: GPTBot\nUser-agent: ClaudeBot\nUser-agent: PerplexityBot\nUser-agent: *\n"
                "Allow: /\nDisallow: /admin/\n\nSitemap: https://monsite.com/sitemap.xml", 'text') +

            "<h2>3. Un résumé pour les IA : llms.txt</h2>"
            "<p><code>/llms.txt</code> est un fichier texte qui résume le site en quelques paragraphes : qui je suis, la liste de mes projets avec un résumé, "
            "mes articles et mes photos. Un assistant IA peut ainsi comprendre l'essentiel sans parcourir chaque page.</p>"

            "<h2>4. Des données structurées</h2>"
            "<p>Chaque page contient un bloc JSON-LD qui décrit son contenu dans un vocabulaire standard (schema.org). "
            "Sur tout le site, une fiche <em>Person</em> donne mon nom, mon métier et ma photo. Sur chaque photo de la galerie, une fiche <em>ImageObject</em> "
            "précise l'auteur, le crédit et le lieu.</p>"

            "<h2>5. Des textes alternatifs qui décrivent vraiment l'image</h2>"
            "<p>Un moteur ne « voit » pas une image : il lit son texte alternatif. « photo1.jpg » ne dit rien ; "
            "« Chadrack Mbu Jess présente Jessna CinéHub sur une TV connectée » dit tout. C'est pourquoi chaque photo de la galerie "
            "a un champ obligatoire qui décrit précisément ce qu'elle montre.</p>"

            "<h2>6. Une belle image de partage</h2>"
            "<p>Les balises <code>og:image</code> choisissent l'image affichée quand une page est partagée sur WhatsApp, Facebook ou LinkedIn. "
            "Au format 1200 × 630 pixels, elle n'est pas recadrée au hasard.</p>"

            "<h2>Et ensuite ?</h2>"
            "<p>Une fois le site en ligne, il reste à déclarer le plan du site dans Google Search Console. "
            "C'est l'étape qui accélère le plus la découverte des pages.</p>"
        ),
    },
]

# Plans d'articles créés par une version précédente de la commande, à remplacer s'ils n'ont pas été modifiés
OLD_DRAFT_SLUGS = [
    'comment-jai-concu-jessna-cinehub',
    'scanner-une-invitation-par-qr-code-avec-django-et-',
    'mettre-en-ligne-un-site-django-sur-pythonanywhere',
]
