from .base import *

DEBUG = True

ALLOWED_HOSTS = []


# Email settings - development

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = "noreply@gamersisland.com"
