import os
from pathlib import Path
from urllib3.util import parse_url
from dotenv import load_dotenv
from django.contrib.messages import constants as messages

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, ".env"))


SECRET_KEY = os.getenv("SECRET_KEY")

FORCE_SCRIPT_NAME = os.getenv("FORCE_SCRIPT_NAME", "")

DEBUG = os.getenv("DEBUG", "False") == "True"

SITE_HOST_SCHEMA = os.getenv("SITE_HOST_SCHEMA", "http")
SITE_HOST_NAME = os.getenv("SITE_HOST_NAME", "localhost")
SITE_HOST_PORT = os.getenv("SITE_HOST_PORT", 8000)

_default_siteurl = (
    "%s://%s:%s/" % (SITE_HOST_SCHEMA, SITE_HOST_NAME, SITE_HOST_PORT)
    if SITE_HOST_PORT
    else "%s://%s/" % (SITE_HOST_SCHEMA, SITE_HOST_NAME)
)
SITEURL = os.getenv("SITEURL", _default_siteurl)

# we need hostname for deployed
_surl = parse_url(SITEURL)
HOSTNAME = _surl.host
SITENAME = os.getenv("SITENAME")

# add trailing slash to site url. geoserver url will be relative to this
if not SITEURL.endswith("/"):
    SITEURL = "{}/".format(SITEURL)

ALLOWED_HOSTS = [
    HOSTNAME,
    SITEURL,
    "localhost",
    "http://localhost:8000",
]


# Application definition

INSTALLED_APPS = [
    "daphne",
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "channels",
    "rest_framework",
    "account",
    "services"
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI_APPLICATION = os.getenv("WSGI_APPLICATION", "core.wsgi.application")
ASGI_APPLICATION = os.getenv("ASGI_APPLICATION", "core.asgi.application")
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "OPTIONS": {"options": "-c search_path=public"},
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    },
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "account.User"


LANGUAGE_CODE = "en-us"

# TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = False


STATIC_URL = "/services/static/"
STATIC_ROOT = os.getenv("STATIC_ROOT", os.path.join(BASE_DIR, "static_root"))
_DEFAULT_STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATICFILES_DIRS = os.getenv("STATICFILES_DIRS", _DEFAULT_STATICFILES_DIRS)

MEDIA_URL = "/services/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# GDAL_LIBRARY_PATH = os.getenv("GDAL_LIBRARY_PATH")
# GEOS_LIBRARY_PATH = os.getenv("GEOS_LIBRARY_PATH")
# PROJ_LIB = os.getenv("PROJ_LIB")

MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "login"
LOGOUT_REDIRECT_URL = "login"

DATE_FORMAT = "Y-m-d"
DATETIME_FORMAT = "'Y-m-d H:i:s"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


X_FRAME_OPTIONS = "ALLOWALL"

XS_SHARING_ALLOWED_METHODS = ["POST", "GET", "OPTIONS", "PUT", "DELETE"]
XS_SHARING_ALLOWED_ORIGINS = "*"

CSRF_COOKIE_SAMESITE = False
CSRF_TRUSTED_ORIGINS = [SITEURL]
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = False

CRISPY_TEMPLATE_PACK = "bootstrap5"


# Define email service

MAIL_TO_ADMIN = os.getenv("MAIL_TO_ADMIN")

EMAIL_ENABLE = False

if EMAIL_ENABLE:
    EMAIL_BACKEND = os.getenv(
        "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
    )

    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_PORT = os.getenv("EMAIL_PORT")
    EMAIL_USE_SSL = True
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
else:
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = os.path.join(BASE_DIR, "emails")


# ILWIS
ILWIS_WORKING_DIR = os.getenv("ILWIS_WORKING_DIR")

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [CELERY_BROKER_URL],
        },
    },
}


# Celery Task Configuration
CELERY_TASK_SERIALIZER = "json"  # Serializer for task messages
CELERY_RESULT_SERIALIZER = "json"  # Serializer for task results
# List of content types accepted for serialization
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = "UTC"  # Timezone for the Celery scheduler


USE_THOUSAND_SEPARATOR = True  # False by default

THOUSAND_SEPARATOR = "\xa0"

ILWIS_API = ""
GEOJAR_FILE = os.path.join(BASE_DIR, "libs/gs/GeoPub.jar")


CORS_ALLOWED_ORIGINS = [
    "https://mara.rangelands.itc.utwente.nl",
    "https://gisedu.itc.utwente.nl",
    "http://localhost",
    "http://127.0.0.1",
]
