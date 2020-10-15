from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_lazy as _
from .management import create_default_wiki


class WikiConfig(AppConfig):

    name = 'apps.wiki'
    verbose_name = _("Wiki")

    def ready(self):
        post_migrate.connect(create_default_wiki, sender=self)
