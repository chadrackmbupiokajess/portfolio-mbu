#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings')
django.setup()

from portfolioapp.models import AdUnit
from portfolioapp.templatetags.portfolio_extras import adsense_unit
from django.test import RequestFactory

def test_adsense_template_tag():
    print("=== Test du template tag adsense_unit ===")
    
    # Créer une fausse requête
    factory = RequestFactory()
    request = factory.get('/')
    context = {'request': request}
    
    # Tester le template tag
    result = adsense_unit(context, 'header')
    
    print(f"Résultat du template tag: {repr(result)}")
    print(f"Longueur du résultat: {len(result)}")
    
    if result:
        print("Code généré:")
        print(result)
    else:
        print("PROBLÈME: Aucun code généré!")
        
        # Vérifier les unités publicitaires
        units = AdUnit.objects.filter(position='header', is_active=True)
        print(f"Unités header trouvées: {units.count()}")
        for unit in units:
            print(f"- {unit.name}: {unit.ad_unit_id}")

if __name__ == "__main__":
    test_adsense_template_tag()