from django.conf import settings


def isascii(s):
    return len(s) == len(s.encode())


def get_available_languages():
    languages = settings.LANGUAGES
    languages.insert(0, (settings.LANGUAGE_CODE, settings.LANGUAGE_NAME))
    return languages
