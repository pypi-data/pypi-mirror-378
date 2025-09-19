from pathlib import Path

from dynaconf import DjangoDynaconf

from .utils import get_settings_files

SECRET_KEY = 'django-insecure_rq-runner'
INSTALLED_APPS = ['rq_result', 'rq_runner']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': Path.cwd() / 'db.sqlite3',
    }
}
TIME_ZONE = 'Asia/Shanghai'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
JOB_MODEL = 'rq_result.Job'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s | %(levelname)-8s | %(name)s - %(message)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {'class': 'logging.NullHandler', 'formatter': 'simple'},
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
        'propagate': False,
    },
}

settings = DjangoDynaconf(
    __name__,
    settings_file=get_settings_files(),
    environments=True,
    load_dotenv=False,
    merge_enabled=True
)

if settings.LOGFILE:
    LOGGING['handlers']['file'] = {
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'filename': settings.LOGFILE,
        'level': 'INFO',
        'formatter': 'simple',
        'when': 'midnight',
        'backupCount': 14,
    }
