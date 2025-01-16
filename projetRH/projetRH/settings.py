# projetRH/settings.py
from pathlib import Path
import os
from datetime import timedelta

# Chemins de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Clé secrète pour le projet (à garder secrète en production)
SECRET_KEY = 'django-insecure-e1zb4i*9y*m0x#&k&3$*xjiwcy(rvji!c0g0=2h34p(-xx9!yl'

# Mode débogage (à désactiver en production)
DEBUG = True

# Liste des hôtes autorisés (à configurer en production)
ALLOWED_HOSTS = []

# Applications installées
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # Framework REST
    'rest_framework_simplejwt',  # Authentification JWT
    'corsheaders',  # Gestion des CORS
    'drf_yasg',  # Documentation Swagger
    'drf_spectacular',  # Documentation OpenAPI
    'core',  # Votre application principale
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Middleware pour CORS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuration des URLs racines
ROOT_URLCONF = 'projetRH.urls'

# Configuration des templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'core/templates')],  # Chemin vers les templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Configuration WSGI
WSGI_APPLICATION = 'projetRH.wsgi.application'

# Configuration de la base de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Validation des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalisation
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Fichiers statiques
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'core/static'),
]

# Fichiers médias
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Clé primaire par défaut
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuration de REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',  # Seuls les utilisateurs authentifiés peuvent accéder aux API
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # Authentification JWT
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',  # Pour la documentation OpenAPI
}

# Configuration de drf-spectacular (documentation OpenAPI)
SPECTACULAR_SETTINGS = {
    'TITLE': 'ProjetRH API',
    'DESCRIPTION': 'Documentation de l\'API du projetRH',
    'VERSION': '1.0.0',
}

# Configuration JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # Durée de vie du token d'accès
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),  # Durée de vie du token de rafraîchissement
    'ROTATE_REFRESH_TOKENS': False,  # Rotation des tokens de rafraîchissement
    'BLACKLIST_AFTER_ROTATION': True,  # Blacklist des anciens tokens après rotation
    'ALGORITHM': 'HS256',  # Algorithme de signature
    'SIGNING_KEY': SECRET_KEY,  # Clé de signature
    'VERIFYING_KEY': None,  # Clé de vérification (optionnelle)
    'AUTH_HEADER_TYPES': ('Bearer',),  # Type de header d'authentification
    'USER_ID_FIELD': 'id',  # Champ utilisé pour l'identifiant utilisateur
    'USER_ID_CLAIM': 'user_id',  # Claim JWT pour l'identifiant utilisateur
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),  # Classes de tokens
    'TOKEN_TYPE_CLAIM': 'token_type',  # Claim JWT pour le type de token
}

# Configuration CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Autoriser les requêtes depuis ce domaine
]

# URL de connexion
LOGIN_URL = '/login/'  # Correspond au chemin de la vue 'login_view'

# Modèle d'utilisateur personnalisé
AUTH_USER_MODEL = 'core.User'  # Utiliser le modèle User personnalisé de l'application core

# Configuration de l'envoi d'e-mails
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Utiliser SMTP pour envoyer des e-mails
EMAIL_HOST = 'smtp.gmail.com'  # Serveur SMTP de Gmail
EMAIL_PORT = 587  # Port SMTP pour TLS
EMAIL_USE_TLS = True  # Activer TLS pour la sécurité
EMAIL_HOST_USER = 'votre_email@gmail.com'  # Votre adresse e-mail
EMAIL_HOST_PASSWORD = 'votre_mot_de_passe'  # Votre mot de passe
DEFAULT_FROM_EMAIL = 'votre_email@gmail.com'  # Adresse e-mail par défaut pour l'envoi