from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolioapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GalleryPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150, verbose_name='Titre')),
                ('slug', models.SlugField(blank=True, help_text='Laissez vide : elle est créée automatiquement à partir du titre.', max_length=170, unique=True, verbose_name='Adresse de la page')),
                ('image', models.ImageField(height_field='height', help_text='JPG ou WebP de préférence, 2000 px de large maximum.', upload_to='galerie/%Y/', verbose_name='Image', width_field='width')),
                ('width', models.PositiveIntegerField(blank=True, editable=False, null=True, verbose_name='Largeur (px)')),
                ('height', models.PositiveIntegerField(blank=True, editable=False, null=True, verbose_name='Hauteur (px)')),
                ('alt_text', models.CharField(help_text="Une phrase précise, lue par Google, les IA et les lecteurs d'écran. Exemple : « Chadrack Mbu Jess présente Jessna CinéHub sur une TV connectée ».", max_length=200, verbose_name="Ce que montre l'image")),
                ('description', models.TextField(blank=True, help_text="Contexte de la photo : où, quand, pourquoi. Plus c'est précis, mieux c'est référencé.", verbose_name='Texte de la page')),
                ('album', models.CharField(blank=True, help_text='Exemple : Événements, Projets, Portraits, Design.', max_length=80, verbose_name='Album')),
                ('location', models.CharField(blank=True, help_text='Exemple : Kinshasa, RDC.', max_length=120, verbose_name='Lieu')),
                ('taken_at', models.DateField(blank=True, null=True, verbose_name='Date de la photo')),
                ('keywords', models.CharField(blank=True, help_text='Séparés par des virgules.', max_length=255, verbose_name='Mots-clés')),
                ('is_published', models.BooleanField(default=True, verbose_name='Publiée')),
                ('is_featured', models.BooleanField(default=False, verbose_name="Afficher sur l'accueil")),
                ('order', models.PositiveIntegerField(default=0, help_text='Plus le nombre est petit, plus la photo apparaît tôt.', verbose_name='Ordre')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Photo de la galerie',
                'verbose_name_plural': 'Galerie photos',
                'ordering': ['order', '-taken_at', '-created_at'],
            },
        ),
    ]
