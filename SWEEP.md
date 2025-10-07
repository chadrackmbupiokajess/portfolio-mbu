# SWEEP.md - Commandes et Règles du Projet

## 🚀 Commandes Django Fréquentes

### Serveur de Développement
```bash
# Démarrer le serveur Django
python manage.py runserver

# Démarrer le serveur sans rechargement automatique
python manage.py runserver --noreload
```

### Migrations
```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer les migrations pour une app spécifique
python manage.py makemigrations portfolioapp
```

### Administration
```bash
# Créer un superutilisateur
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic
```

## 🔧 Résolution de Problèmes

### Template Tags
- **Problème** : `TemplateSyntaxError` avec les template tags personnalisés
- **Solution** : Redémarrer le serveur Django (Ctrl+C puis `python manage.py runserver`)
- **Cause** : Django met en cache les template tags et ne les recharge pas automatiquement

### AdSense Integration
- Les template tags AdSense sont définis dans `portfolioapp/templatetags/portfolio_extras.py`
- Toujours redémarrer le serveur après avoir ajouté de nouveaux template tags
- Vérifier que `{% load portfolio_extras %}` est présent en haut des templates

## 📁 Structure du Projet
```
portfolio/
├── portfolioapp/
│   ├── templatetags/
│   │   ├── __init__.py
│   │   └── portfolio_extras.py
│   ├── models.py (contient les modèles AdSense)
│   └── admin.py (contient l'admin AdSense)
├── templates/
│   └── portfolioapp/
│       ├── base.html
│       └── tags/
│           └── adsense_banner.html
└── manage.py
```

## 🎯 Règles de Développement
- Toujours tester les template tags après redémarrage du serveur
- Utiliser le mode test AdSense pendant le développement
- Vérifier les migrations avant de déployer en production