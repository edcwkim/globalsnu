from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from apps.core.views import Autocomplete, Home, Manual, Manual2

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('manual/', Manual.as_view(), name='manual'),
    path('manual/2/', Manual2.as_view(), name='manual_2'),
    path('about/', TemplateView.as_view(template_name="core/about.html"), name='about'),
    path('tos/', TemplateView.as_view(template_name="core/tos.html"), name='tos'),
    path('privacy/', TemplateView.as_view(template_name="core/privacy.html"), name='privacy'),
    path('copyright/', TemplateView.as_view(template_name="core/copyright.html"), name='copyright'),
    path('autocomplete/<path:scope>/', Autocomplete.as_view(), name='autocomplete'),

    path('django-admin/', admin.site.urls),

    path('', include('apps.auth.urls')),
    path('', include('apps.univ.urls')),
    path('', include('apps.wiki.urls')),
]
