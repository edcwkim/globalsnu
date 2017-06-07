from django.apps import apps as global_apps
from django.conf import settings
from django.core.management.color import no_style
from django.db import DEFAULT_DB_ALIAS, connections, router


def create_default_wiki(app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs):
    # see django.contrib.sites.management
    try:
        Wiki = apps.get_model('wiki', 'Wiki')
    except LookupError:
        return

    if not router.allow_migrate_model(using, Wiki):
        return

    if not Wiki.objects.using(using).exists():
        LANGUAGE_CODE = getattr(settings, 'LANGUAGE_CODE', '')
        LANGUAGE_NAME = getattr(settings, 'LANGUAGE_NAME', '')
        if verbosity >= 2:
            print("Creating {} Wiki object".format(LANGUAGE_NAME))
        Wiki(pk=1, lang=LANGUAGE_CODE).save(using=using)
        sequence_sql = connections[using].ops.sequence_reset_sql(no_style(), [Wiki])
        if sequence_sql:
            if verbosity >= 2:
                print("Resetting sequence")
            with connections[using].cursor() as cursor:
                for command in sequence_sql:
                    cursor.execute(command)
