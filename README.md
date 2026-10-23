# Gestion d’Astreintes — Django

Application web de gestion des plannings d’astreinte, avec génération automatique de PDF et envoi par email aux collaborateurs.

🔗 Repository GitHub : gestion-astreintes-django
## Présentation

Gestion d’Astreintes est une application web développée avec Django et Python pour simplifier la gestion des périodes d’astreinte au sein d’une organisation.

Elle permet de centraliser les informations des collaborateurs, de planifier les astreintes, de générer des documents PDF personnalisés et de transmettre les plannings par email.

L’objectif est de réduire les tâches manuelles, d’améliorer la communication et de faciliter le suivi des astreintes.

## Fonctionnalités principales

- Gestion des collaborateurs : ajout, modification, consultation et suppression.
- Gestion des astreintes : création et suivi des périodes d’astreinte.
- Tableau de bord : aperçu des collaborateurs, des astreintes et des prochaines périodes.
- Génération de PDF : création de documents contenant les informations du planning.
- Envoi par email : transmission des PDF aux collaborateurs concernés.
- Automatisation : possibilité de planifier l’envoi des documents.
- Interface web : gestion centralisée des données depuis un navigateur


## Stack technique

- Python 3
- Django 5.2
- MySQL
- HTML / CSS / JavaScript
- Bootstrap 
## Structure du projet

```text
gestion-astreintes-django/
├── accounts/
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── admin_app/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/
├── templates/
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Prérequis

Avant de lancer le projet, assurez-vous d’avoir installé :

- Python 3.10+
- pip
- MySQL Server
- Un environnement virtuel Python

## Installation

1. Cloner le dépôt :

```bash
git clone https://github.com/hmzelhmr/gestion-astreintes-django.git
cd gestion-astreintes-django
```

2. Créer et activer un environnement virtuel :

```bash
python -m venv venv
venv\Scripts\activate      # Windows
```

3. Installer les dépendances :

```bash
pip install -r requirements.txt
```

4. Configurer la base de données :

Modifier le fichier `admin_app/settings.py` et renseigner les paramètres de connexion MySQL :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nom_de_la_base',
        'USER': 'utilisateur',
        'PASSWORD': 'mot_de_passe',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

5. Générer les tables de la base de données :

```bash
python manage.py migrate
```

6. Créer un superutilisateur :

```bash
python manage.py createsuperuser
```

7. Lancer le serveur de développement :

```bash
python manage.py runserver
```

Le projet est ensuite accessible à l’adresse :

```text
http://127.0.0.1:8000/
```

## Configuration SMTP (e-mail)

Le projet inclut une configuration SMTP dans `admin_app/settings.py` pour l’envoi d’e-mails. Il est recommandé de remplacer les valeurs de démonstration par vos propres identifiants de messagerie ou d’utiliser des variables d’environnement pour sécuriser les informations sensibles.

Exemple :

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "votre_email"
EMAIL_HOST_PASSWORD = "votre_mot_de_passe_app"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

## Variables de sécurité

Le fichier `settings.py` contient également une clé secrète vide (`SECRET_KEY = ''`). Pour un environnement de production, il est impératif de la remplacer par une valeur sécurisée et de ne pas la laisser vide.

## Utilisation

- Accéder au site via le navigateur
- Se connecter avec un compte utilisateur ou un superutilisateur
- Gérer les comptes et les droits depuis l’interface Django
- Étendre les fonctionnalités selon les exigences métier

## Bonnes pratiques

- Ne jamais committer les identifiants sensibles
- Utiliser les variables d’environnement en production
- Séparer les configurations de développement et de production
- Vérifier régulièrement les migrations Django

## Licence

Ce projet n’a pas de licence explicitement définie dans le dépôt. 

## Auteur

Projet développé dans le cadre de mon stage d'observation au sien de 'OCP Group' dans le cadre de la gestion des utilisateurs et des accès avec Django.

---
