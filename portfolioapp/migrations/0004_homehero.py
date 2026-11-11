from django.db import migrations, models


DEFAULT_HERO_TEXT = (
    "Je conçois et développe des applications web sur mesure, du site vitrine à la plateforme complète : "
    "une base de code soignée, des interfaces claires et un produit qui tient la route une fois en ligne."
)


class Migration(migrations.Migration):

    dependencies = [
        ('portfolioapp', '0003_project_date_realisation'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomeHero',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Chadrack Mbu Jess', max_length=80, verbose_name='Nom affiché')),
                ('role', models.CharField(default='Développeur full-stack', help_text='Affiché en doré sous le nom. Exemple : Développeur full-stack et designer.', max_length=120, verbose_name='Métier')),
                ('intro', models.TextField(default=DEFAULT_HERO_TEXT, help_text='2 ou 3 phrases maximum : ce que vous faites et pour qui.', verbose_name='Texte de présentation')),
                ('photo', models.ImageField(blank=True, help_text='Photo carrée de préférence (au moins 800 × 800 px). Laissez vide pour garder la photo actuelle.', upload_to='accueil/', verbose_name='Photo')),
                ('photo_alt', models.CharField(default='Portrait de Chadrack Mbu Jess', help_text="Lue par Google et les lecteurs d'écran.", max_length=150, verbose_name='Description de la photo')),
                ('primary_label', models.CharField(default='Voir mes projets', max_length=40, verbose_name='Bouton principal : texte')),
                ('primary_url', models.CharField(blank=True, help_text='Laissez vide pour la page Projets. Exemple : /galerie/ ou https://…', max_length=200, verbose_name='Bouton principal : lien')),
                ('secondary_label', models.CharField(blank=True, default='Me contacter', help_text='Laissez vide pour masquer ce bouton.', max_length=40, verbose_name='Bouton secondaire : texte')),
                ('secondary_url', models.CharField(blank=True, help_text='Laissez vide pour la page Contact.', max_length=200, verbose_name='Bouton secondaire : lien')),
                ('technologies', models.CharField(blank=True, default='Python, Django, JavaScript', help_text='Ligne affichée sous les boutons. Laissez vide pour la masquer.', max_length=150, verbose_name='Technologies')),
                ('show_projects_count', models.BooleanField(default=True, verbose_name='Afficher le nombre de projets')),
                ('show_cv', models.BooleanField(default=True, help_text='Nécessite un CV ajouté dans la rubrique CV.', verbose_name='Afficher le lien vers le CV')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Dernière modification')),
            ],
            options={
                'verbose_name': 'Accueil : en-tête',
                'verbose_name_plural': 'Accueil : en-tête',
            },
        ),
    ]
