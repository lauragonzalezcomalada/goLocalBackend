from .base import *
import os

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Opcional: usar SQLite en local
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST", "db"),  # <- "db" es el nombre del servicio
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}