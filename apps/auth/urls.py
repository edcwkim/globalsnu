from django.urls import include, re_path, path
from django.contrib.auth import views as django_views
from django.views.generic.base import RedirectView, TemplateView
from . import views

urlpatterns = [
    path('login/', RedirectView.as_view(pattern_name='home', query_string=True), name='login'),
    path('logout/', django_views.LogoutView.as_view(), name='logout'),

    path('password/reset/', include([
        path('', django_views.PasswordResetView.as_view(), name='password_reset'),
        path('sent/', django_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
        re_path(r'^(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            django_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
        path('done/', django_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    ])),

    path('register/', views.Register.as_view(), name='register'),
    path('register/verify/', TemplateView.as_view(template_name="registration/register_verify.html"), name='register_verify'),
    path('verify/<path:sign>/', views.Verify.as_view(), name='verify'),

    path('you/', include([
        path('', RedirectView.as_view(pattern_name='favorites'), name='profile'),
        path('favorites/', views.Favorites.as_view(), name='favorites'),
        path('edits/', views.PersonalEdits.as_view(), name='personal_edits'),
        path('settings/', include([
            path('', views.Settings.as_view(), name='settings'),
            path('nickname/', views.NicknameChange.as_view(), name='nickname_change'),
            path('deactivate/', views.Deactivate.as_view(), name='deactivate'),
        ])),
    ])),
]
