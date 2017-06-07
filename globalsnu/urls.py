from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
from .core.views import Autocomplete, Home, Manual, Manual2

urlpatterns = [
    url(r'^$', Home.as_view(), name='home'),
    url(r'^manual/$', Manual.as_view(), name='manual'),
    url(r'^manual/2/$', Manual2.as_view(), name='manual_2'),
    url(r'^about/$', TemplateView.as_view(template_name="core/about.html"), name='about'),
    url(r'^tos/$', TemplateView.as_view(template_name="core/tos.html"), name='tos'),
    url(r'^privacy/$', TemplateView.as_view(template_name="core/privacy.html"), name='privacy'),
    url(r'^copyright/$', TemplateView.as_view(template_name="core/copyright.html"), name='copyright'),
    url(r'^autocomplete/(?:(?P<scope>[^/]+)/)?$', Autocomplete.as_view(), name='autocomplete'),

    url(r'^django-admin/', admin.site.urls),

    url(r'^', include('globalsnu.auth.urls')),
    url(r'^', include('globalsnu.univ.urls', namespace='univ')),
    url(r'^', include('globalsnu.wiki.urls', namespace='wiki')),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
