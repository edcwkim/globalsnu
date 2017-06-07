from django.conf.urls import include, url
from django.contrib.auth import views as django_views
from django.views.generic.base import RedirectView, TemplateView
from . import views

urlpatterns = [
    url(r'^login/$', RedirectView.as_view(pattern_name='home', query_string=True), name='login'),
    url(r'^logout/$', django_views.LogoutView.as_view(), name='logout'),

    url(r'^password/reset/', include([
        url(r'^$', django_views.PasswordResetView.as_view(), name='password_reset'),
        url(r'^sent/$', django_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
        url(r'^(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            django_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
        url(r'^done/$', django_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    ])),

    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^register/verify/$', TemplateView.as_view(template_name="registration/register_verify.html"), name='register_verify'),
    url(r'^verify/(?P<sign>[^/]+)/$', views.Verify.as_view(), name='verify'),

    url(r'^you/', include([
        url(r'^$', RedirectView.as_view(pattern_name='favorites'), name='profile'),
        url(r'^favorites/$', views.Favorites.as_view(), name='favorites'),
        url(r'^edits/$', views.PersonalEdits.as_view(), name='personal_edits'),
        url(r'^settings/', include([
            url(r'^$', views.Settings.as_view(), name='settings'),
            url(r'^nickname/$', views.NicknameChange.as_view(), name='nickname_change'),
            url(r'^deactivate/$', views.Deactivate.as_view(), name='deactivate'),
        ])),
    ])),
]
