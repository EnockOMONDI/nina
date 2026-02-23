from pathlib import Path

from decouple import config
from dotenv import load_dotenv
import dj_database_url
from . import admin_nav

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = config('SECRET_KEY', default='change-me')
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_ckeditor_5',
    'crispy_forms',
    'import_export',
    'taggit',
    'rest_framework',
    'adminside',
    'users',
    'blog',
    'status',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tours_travels.urls'

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

WSGI_APPLICATION = 'tours_travels.wsgi.application'

DATABASE_URL = config('DATABASE_URL', default='')
DB_CONN_MAX_AGE = config('DB_CONN_MAX_AGE', default=600, cast=int)
DB_CONN_HEALTH_CHECKS = config('DB_CONN_HEALTH_CHECKS', default=True, cast=bool)
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=DB_CONN_MAX_AGE,
            conn_health_checks=DB_CONN_HEALTH_CHECKS,
        )
    }
else:
    db_name = config('DB_NAME', default='')
    if db_name:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': db_name,
                'USER': config('DB_USER', default=''),
                'PASSWORD': config('DB_PASSWORD', default=''),
                'HOST': config('DB_HOST', default=''),
                'PORT': config('DB_PORT', default=''),
                'CONN_MAX_AGE': DB_CONN_MAX_AGE,
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = config('TIME_ZONE', default='UTC')
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_PROVIDER = config("EMAIL_PROVIDER", default="smtp")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL", default="Ziada Tours and Travel.com <info@ziadatoursandtravel.com>"
)
ADMIN_EMAIL = config("ADMIN_EMAIL", default="info@ziadatoursandtravel.com")
JOBS_EMAIL = config("JOBS_EMAIL", default=ADMIN_EMAIL)
NEWSLETTER_EMAIL = config("NEWSLETTER_EMAIL", default=ADMIN_EMAIL)
EXTRA_EMAIL_RECIPIENTS = config(
    "EXTRA_EMAIL_RECIPIENTS",
    default="",
).split(",")
SITE_URL = config("SITE_URL", default="http://127.0.0.1:8000")
WHATSAPP_PHONE = config("WHATSAPP_PHONE", default="")
MAILTRAP_API_TOKEN = config("MAILTRAP_API_TOKEN", default="")
BREVO_API_KEY = config("BREVO_API_KEY", default="")
BREVO_SENDER_EMAIL = config("BREVO_SENDER_EMAIL", default="")
BREVO_SENDER_NAME = config("BREVO_SENDER_NAME", default="Ziada Tours and Travel")

EMAIL_HOST = config("EMAIL_HOST", default="smtp-relay.brevo.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_TIMEOUT = config("EMAIL_TIMEOUT", default=10, cast=int)

EMAIL_RATE_LIMIT_PER_MINUTE = config("EMAIL_RATE_LIMIT_PER_MINUTE", default=60, cast=int)
EMAIL_RATE_LIMIT_PER_HOUR = config("EMAIL_RATE_LIMIT_PER_HOUR", default=100, cast=int)

GOOGLE_ANALYTICS_ID = config("GOOGLE_ANALYTICS_ID", default="")
GOOGLE_TAG_MANAGER_ID = config("GOOGLE_TAG_MANAGER_ID", default="")
ENABLE_ANALYTICS = config("ENABLE_ANALYTICS", default=False, cast=bool)
ANALYTICS_TRACK_ADMIN = config("ANALYTICS_TRACK_ADMIN", default=False, cast=bool)

UPLOADCARE_PUBLIC_KEY = config("UPLOADCARE_PUBLIC_KEY", default="")
UPLOADCARE_SECRET_KEY = config("UPLOADCARE_SECRET_KEY", default="")

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "|",
            "undo",
            "redo",
            "alignment",
            "outdent",
            "indent",
            "|",
            "imageUpload",
            "insertTable",
            "mediaEmbed",
            "codeBlock",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "imageStyle:full",
                "imageStyle:side",
            ]
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
            ]
        },
    }
}

UNFOLD = {
    "SITE_TITLE": "Ziada Travel",
    "SITE_HEADER": "Ziada Travel Admin",
    "SITE_SUBHEADER": "Simple site control",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Travel Content",
                "items": [
                    {"title": "Packages", "link": admin_nav.adminside_package_list},
                    {"title": "Hotels", "link": admin_nav.adminside_hotel_list},
                    {"title": "Blog Posts", "link": admin_nav.blog_post_list},
                    {"title": "Blog Categories", "link": admin_nav.blog_category_list},
                ],
            },
            {
                "title": "Clients & Messages",
                "items": [
                    {"title": "Contact Inquiries", "link": admin_nav.users_contact_list},
                    {"title": "Corporate Inquiries", "link": admin_nav.users_corporate_list},
                    {"title": "MICE Inquiries", "link": admin_nav.users_mice_list},
                    {"title": "Student Travel", "link": admin_nav.users_student_list},
                    {"title": "NGO Travel", "link": admin_nav.users_ngo_list},
                ],
            },
            {
                "title": "System Status",
                "items": [
                    {"app": "status"},
                ],
            },
            {
                "title": "Manage Users",
                "items": [
                    {"title": "Users", "link": admin_nav.auth_user_list},
                    {"title": "Groups", "link": admin_nav.auth_group_list},
                ],
            },
        ],
    },
}
