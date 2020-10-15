from django.urls import include, path
from django.views.generic import TemplateView
from . import views

app_name = 'wiki'

urlpatterns = [
    path('pages/', views.PageList.as_view(), name='page_list'),
    path('essays/', views.EssayList.as_view(), name='essay_list'),
    path('w/', include([
        path('guide/', TemplateView.as_view(template_name="wiki/guide.html"), name='guide'),
        path('create/', views.PageCreate.as_view(), name='page_create'),
        path('random/', views.PageRandom.as_view(), name='page_random'),
    ])),
    path('<path:title>/', include([
        path('', views.PageDetail.as_view(), name='page_detail'),
        path('history/', views.PageHistory.as_view(), name='page_history'),
        path('history/<int:revision_number>/', views.PageRevisionDetail.as_view(), name='page_revision_detail'),
        path('edit/', views.PageUpdate.as_view(), name='page_update'),
        path('edit/title/', views.PageTitleUpdate.as_view(), name='page_title_update'),
        path('write/', views.EssayCreate.as_view(), name='essay_create'),
    ])),
    path('essay/', include([
        path('like/', views.EssayLike.as_view(), name='essay_like'),
        path('<int:pk>/', views.EssayDetail.as_view(), name='essay_detail'),
        path('<int:pk>/edit/', views.EssayUpdate.as_view(), name='essay_update'),
    ])),
]
