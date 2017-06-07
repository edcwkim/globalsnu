from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AuthConfig(AppConfig):

    name = 'globalsnu.auth'
    label = 'auth_'
    verbose_name = _("Authentication and Authorization")
