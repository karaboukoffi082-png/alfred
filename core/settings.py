import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'dkpress-cle-secrete-temporaire-a-changer-en-production-xyz123'
DEBUG = True
ALLOWED_HOSTS = ['*']
AUTH_USER_MODEL = 'users.User'
INSTALLED_APPS = [
    #'daphne', # Obligatoire en premier pour les WebSockets
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Apps tierces
    'rest_framework',
    'corsheaders',
    'django_filters',
    'channels',
    
    # Apps DK-PRESS
    'users.apps.UsersConfig',
    'pages.apps.PagesConfig',
    'shop.apps.ShopConfig',
    'pressing.apps.PressingConfig',
    'fai.apps.FaiConfig',
    'chat.apps.ChatConfig',
    'delivery.apps.DeliveryConfig',
    'payments.apps.PaymentsConfig',
    'notifications.apps.NotificationsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

ASGI_APPLICATION = 'core.asgi.application'

# Base de données PostgreSQL
# Base de données PostgreSQL (Temporairement hardcodé pour tester)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'alfred_db',
        'USER': 'postgres',       # <-- À modifier si tu utilises un autre nom d'utilisateur dans pgAdmin
        'PASSWORD': 'KARa@40bou',
        'HOST': 'localhost',      # <-- ou '127.0.0.1'
        'PORT': '5432',           # <-- Port par défaut de PostgreSQL
    }
}
# Redis & Channels (WebSockets)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
        "hosts": ["redis://127.0.0.1:6379/0"],
        },
    },
}
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
    }
}

# Fichiers statiques et médias
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Lome'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Configuration Mobile Money (à remplacer par les vraies valeurs plus tard)
# Nouvelles valeurs pour PayGateGlobal
PAYGATE_API_KEY = "b1fa0068-63fc-4c6b-9d72-acc17227a997"
# Optionnel : URL de base (si vous voulez la rendre configurable)
PAYGATE_BASE_URL = "https://paygateglobal.com/api/v1"
# Authentification
AUTH_USER_MODEL = 'users.User'
LOGIN_URL = '/compte/connexion/'
LOGIN_REDIRECT_URL = '/compte/tableau-de-bord/'
LOGOUT_REDIRECT_URL = '/'