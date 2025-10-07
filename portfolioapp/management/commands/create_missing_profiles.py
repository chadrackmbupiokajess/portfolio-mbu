from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from portfolioapp.models import Profile

class Command(BaseCommand):
    help = 'Crée les profils manquants pour tous les utilisateurs existants'

    def handle(self, *args, **options):
        users_without_profile = []
        users_with_profile = []
        
        for user in User.objects.all():
            try:
                # Vérifier si l'utilisateur a un profil
                profile = user.profile
                users_with_profile.append(user.username)
            except Profile.DoesNotExist:
                # Créer un profil pour cet utilisateur
                Profile.objects.create(user=user)
                users_without_profile.append(user.username)
                self.stdout.write(
                    self.style.SUCCESS(f'Profil créé pour l\'utilisateur: {user.username}')
                )
        
        # Résumé
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Utilisateurs avec profil existant: {len(users_with_profile)}')
        if users_with_profile:
            for username in users_with_profile:
                self.stdout.write(f'  - {username}')
        
        self.stdout.write(f'\nProfils créés: {len(users_without_profile)}')
        if users_without_profile:
            for username in users_without_profile:
                self.stdout.write(f'  - {username}')
        
        if users_without_profile:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ {len(users_without_profile)} profil(s) créé(s) avec succès!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✅ Tous les utilisateurs ont déjà un profil!')
            )