from .base import *
import dj_database_url
from decouple import config
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

DATABASES = {
    'default': dj_database_url.config(default='postgresql://golocalbackend_staging_user:vFySJwYrgST8yKCIlqbxiecHVOvpJ0VB@dpg-d2osaqripnbc73a6onpg-a/golocalbackend_staging')
}

MEDIA_URL = '/media/'

ROOT_URLCONF = "worldwild_backend.urls"

DEBUG = False
ALLOWED_HOSTS = ['golocalbackend.onrender.com','127.0.0.1']

# Logs en consola para revisar staging
LOGGING = {
    "version": 1,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
