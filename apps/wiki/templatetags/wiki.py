from bs4 import BeautifulSoup
from django import template
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.shortcuts import resolve_url
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from markdown import markdown as md
from markdown.extensions.toc import TocExtension
from markdown.extensions.wikilinks import WikiLinkExtension
from apps.wiki.models import Page
from apps.wiki.views import get_current_wiki


register = template.Library()


def slugify(value, separator):
    return value.replace(' ', separator)

def url_builder(label, base, end):
    try:
        page = Page.objects.get(wiki=get_current_wiki(),
            current_revision__title=label)
        return resolve_url(page)
    except MultipleObjectsReturned:
        page = Page.objects.get(wiki=get_current_wiki(),
            title_for_url=label.replace(' ', '_'))
        return resolve_url(page)
    except ObjectDoesNotExist:
        return resolve_url('wiki:page_create') + '?title=' + label.replace(' ', '_')

@register.filter(needs_autoescape=True)
def markdown(value, autoescape=True):
    value = conditional_escape(value) if autoescape else value
    value = md(value, output_format='html5', tab_length=2, extensions=[
        TocExtension(
            baselevel=2,
            slugify=slugify,
            separator='_',
            permalink=' ',
            marker='[목차]',
            title='목차',
        ),
        WikiLinkExtension(
            build_url=url_builder,
        ),
        'markdown.extensions.sane_lists',
        'markdown.extensions.nl2br',
    ])
    return mark_safe(value)


acceptable_elements = ['a', 'abbr', 'acronym', 'address', 'area', 'b', 'big',
    'blockquote', 'br', 'button', 'caption', 'center', 'cite', 'code', 'col',
    'colgroup', 'dd', 'del', 'dfn', 'dir', 'div', 'dl', 'dt', 'em', 'font',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'ins', 'kbd', 'label',
    'legend', 'li', 'map', 'menu', 'ol', 'p', 'pre', 'q', 's', 'samp', 'small',
    'span', 'strike', 'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot',
    'th', 'thead', 'tr', 'tt', 'u', 'ul', 'var']

acceptable_attributes = ['abbr', 'accept', 'accept-charset', 'accesskey',
    'action', 'align', 'alt', 'axis', 'border', 'cellpadding', 'cellspacing',
    'char', 'charoff', 'charset', 'checked', 'cite', 'clear', 'cols', 'colspan',
    'color', 'compact', 'coords', 'datetime', 'dir', 'enctype', 'for',
    'headers', 'height', 'href', 'hreflang', 'hspace', 'id', 'ismap', 'label',
    'lang', 'longdesc', 'maxlength', 'method', 'multiple', 'name', 'nohref',
    'noshade', 'nowrap', 'prompt', 'rel', 'rev', 'rows', 'rowspan', 'rules',
    'scope', 'shape', 'size', 'span', 'src', 'start', 'summary', 'tabindex',
    'target', 'title', 'type', 'usemap', 'valign', 'value', 'vspace', 'width']

@register.filter
@stringfilter
def richtext(value):
    while True:
        soup = BeautifulSoup(value, "html.parser")
        removed = False
        for tag in soup.find_all(True):  # find all tags
            if tag.name not in acceptable_elements:
                tag.extract()  # remove the bad ones
                removed = True
            else:  # it might have bad attributes
                keys = list(tag.attrs.keys())
                for key in keys:
                    if key not in acceptable_attributes:
                        del tag[key]
                        removed = True
        value = str(soup)  # turn it back to html
        if not removed:
            break
    if value.endswith('</br>'):
        value = value[:-5]
    return mark_safe(value)
