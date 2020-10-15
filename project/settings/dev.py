from . import *  # noqa

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=-kx7^0-yu7o*&hcf!q27%*1zswvu3_2fgl03316znt$b(6u$h'

VERIFICATION_SALT = SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

for template in TEMPLATES:  # noqa
    template['OPTIONS']['debug'] = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
