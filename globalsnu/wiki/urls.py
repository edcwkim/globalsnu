from django.conf.urls import include, url
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    url(r'^pages/$', views.PageList.as_view(), name='page_list'),
    url(r'^essays/$', views.EssayList.as_view(), name='essay_list'),
    url(r'^w/', include([
        url(r'^guide/$', TemplateView.as_view(template_name="wiki/guide.html"), name='guide'),
        url(r'^create/$', views.PageCreate.as_view(), name='page_create'),
        url(r'^random/$', views.PageRandom.as_view(), name='page_random'),
    ])),
    url(r'^(?P<title>[^/]+)/', include([
        url(r'^$', views.PageDetail.as_view(), name='page_detail'),
        url(r'^history/$', views.PageHistory.as_view(), name='page_history'),
        url(r'^history/(?P<revision_number>\d+)/$', views.PageRevisionDetail.as_view(), name='page_revision_detail'),
        url(r'^edit/$', views.PageUpdate.as_view(), name='page_update'),
        url(r'^edit/title/$', views.PageTitleUpdate.as_view(), name='page_title_update'),
        url(r'^write/$', views.EssayCreate.as_view(), name='essay_create'),
    ])),
    url(r'^essay/', include([
        url(r'^like/$', views.EssayLike.as_view(), name='essay_like'),
        url(r'^(?P<pk>\d+)/$', views.EssayDetail.as_view(), name='essay_detail'),
        url(r'^(?P<pk>\d+)/edit/$', views.EssayUpdate.as_view(), name='essay_update'),
    ])),
]
