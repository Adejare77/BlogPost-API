import logging
import os
from datetime import timedelta
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    TESTING=(bool, False),
    SECRET_KEY=(str, environ.Env.NOTSET),
    ALLOWED_HOSTS=(list, ["localhost"]),
    LOG_SAMPLING_RATE=(float, 0.1),
    PROMETHEUS_TOKEN=(str, ""),
)

# read the .env file
if os.path.exists(BASE_DIR / ".env"):
    environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
DEBUG = env("DEBUG")
LOG_SAMPLING_RATE = max(0, min(1, env("LOG_SAMPLING_RATE")))
LOG_SAMPLING = not DEBUG
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
PROMETHEUS_SCRAPE_TOKEN = env("PROMETHEUS_TOKEN")
PROMETHEUS_TOKEN_FILE = "/run/secrets/prometheus_scrape_token"
TESTING = env("TESTING")

# retrieve prometheus token
try:
    with open(PROMETHEUS_TOKEN_FILE) as f:
        PROMETHEUS_SCRAPE_TOKEN = f.read().strip()
except FileNotFoundError:
    if DEBUG and not PROMETHEUS_SCRAPE_TOKEN:
        raise RuntimeError("DEBUG mode: PROMETHEUS_TOKEN missing from .env")
    elif DEBUG:
        pass
    else:
        raise RuntimeError(
            "Production error: Prometheus token secret not mounted at "
            f"{PROMETHEUS_TOKEN_FILE}. NEVER use .env in production."
        )

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_filters",
    "drf_spectacular",
    "rest_framework",
    "corsheaders",
    "app.core",
    "app.user",
    "app.post",
    "app.like",
    "app.comment",
    "app.utils",
    "rest_framework_simplejwt.token_blacklist",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "app.core.middleware.monitoring.middleware.PrometheusMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "app.core.middleware.logging.RequestResponseLoggingMiddleware",
]

CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

ROOT_URLCONF = "blogPost.urls"

if DEBUG:
    DEFAULT_THROTTLE_RATES = {
        "anon": "100000/min",
        "user": "100000/min",
        "auth_login": "100000/min",
        "auth_register": "100000/min",
        "auth_password_reset": "100000/min",
    }
else:
    DEFAULT_THROTTLE_RATES = {
        "anon": "60/min",
        "user": "120/min",
        "auth_login": "5/min",
        "auth_register": "3/min",
        "auth_password_reset": "2/min",
    }


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_RENDERER_CLASSES": (
        ["rest_framework.renderers.JSONRenderer"]
        if not DEBUG
        else [
            "rest_framework.renderers.JSONRenderer",
            "rest_framework.renderers.BrowsableAPIRenderer",
        ]
    ),
    "DEFAULT_THROTTLE_CLASSES": [
        "app.core.security.throttling.general.UserThrottling",
        "app.core.security.throttling.general.AnonThrottling",
    ],
    "DEFAULT_THROTTLE_RATES": DEFAULT_THROTTLE_RATES,
}


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "blogPost.wsgi.application"


if env("TESTING"):
    DATABASES = {
        "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
    }
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
else:
    DATABASES = {"default": env.db()}  # reads all in the .env


# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": f"redis://{"localhost" if TESTING else "redis"}:6379/1",
#         "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Register the User Model
AUTH_USER_MODEL = "user.User"

# Auto take care of end slashes
APPEND_SLASH = True

# Simple JWT settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Rashisky BlogPost APIs",
    "DESCRIPTION": "API for Post, Comments",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[{levelname}] {asctime} {name}: {message}",
            "style": "{",
        },
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": "%(levelname)s %(asctime)s %(name)s: %(message)s",
        },
    },
    "filters": {
        "only_info": {
            "()": "django.utils.log.CallbackFilter",
            "callback": lambda record: record.levelno == logging.INFO,
        }
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "standard"},
        "app_handler": {
            "class": "logging.FileHandler",
            "formatter": "json",
            "filename": LOG_DIR / "api.log",
            "level": "INFO",
        },
        "error_handler": {
            "class": "logging.FileHandler",
            "formatter": "json",
            "filename": LOG_DIR / "error.log",
            "level": "WARNING",
        },
        "django_handler": {
            "class": "logging.FileHandler",
            "formatter": "json",
            "filename": LOG_DIR / "django.log",
            "level": "ERROR",
        },
        "request_handler": {
            "class": "logging.FileHandler",
            "formatter": "json",
            "filename": LOG_DIR / "request.log",
            "level": "INFO",
            "filters": ["only_info"],
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "django_handler"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "error_handler"],
            "level": "WARNING",
            "propagate": False,
        },
        "app": {
            "handlers": ["console", "app_handler"],
            "level": "INFO",
            "propagate": False,
        },
        "request_logger": {
            "handlers": ["console", "request_handler", "error_handler"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
