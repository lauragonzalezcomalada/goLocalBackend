from .base import *

DEBUG = False
ALLOWED_HOSTS = ["api.tuapp.com", "tuapp.com"]

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Logs más estrictos
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": "/var/log/django/error.log",
        },
    },
    "loggers": {
        "django": {"handlers": ["file"], "level": "WARNING", "propagate": True},
    },
}
