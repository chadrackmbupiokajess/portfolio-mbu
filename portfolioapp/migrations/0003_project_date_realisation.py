from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolioapp', '0002_galleryphoto'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='date_realisation',
            field=models.DateField(blank=True, help_text="Mois de fin du projet (ou de début s'il est en cours). Seuls le mois et l'année sont affichés. Laissez vide pour utiliser la date d'ajout sur le site.", null=True, verbose_name='Date de réalisation'),
        ),
    ]
