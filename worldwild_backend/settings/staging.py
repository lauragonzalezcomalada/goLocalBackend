from .base import *
import dj_database_url

DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL")
    )
}

DATABASES = {
    'default': dj_database_url.config(default='postgresql://golocalbackend_staging_user:vFySJwYrgST8yKCIlqbxiecHVOvpJ0VB@dpg-d2osaqripnbc73a6onpg-a/golocalbackend_staging')
}



DEBUG = False
ALLOWED_HOSTS = ["https://golocalbackend.onrender.com"]

# Logs en consola para revisar staging
LOGGING = {
    "version": 1,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
