import re
from django import urls
from django.conf import settings
from django.utils.translation import get_language


class LocaleRegexURLResolver(urls.LocaleRegexURLResolver):
    """
    A customized URL resolver that does not prepend language code for the
    primary language (Korean). Otherwise, it prepends language codes as usual.
    """

    @property
    def regex(self):
        language_code = get_language()
        if language_code not in self._regex_dict:
            regex_compiled = (re.compile('', re.UNICODE)
                              if language_code == settings.LANGUAGE_CODE
                              else re.compile('^%s/' % language_code, re.UNICODE))
            self._regex_dict[language_code] = regex_compiled
        return self._regex_dict[language_code]
