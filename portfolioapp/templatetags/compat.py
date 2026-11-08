"""
Compatibilité avec django-material-admin.

Le thème d'administration utilise le filtre « length_is », supprimé dans Django 5.1.
Ce module le rétablit pour tous les templates (déclaré dans settings.TEMPLATES['OPTIONS']['builtins']).
"""
from django import template

register = template.Library()


@register.filter(is_safe=False)
def length_is(value, arg):
    """Renvoie True si la longueur de la valeur est égale à l'argument."""
    try:
        return len(value) == int(arg)
    except (ValueError, TypeError):
        return ""
