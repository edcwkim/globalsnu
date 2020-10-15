from django.urls import include, path
from . import views

app_name = 'univ'

urlpatterns = [
    path('snuinworld/', views.SNUInWorldList.as_view(), name="snu_in_world"),
    path('snuinworld/<str:topic>/', views.SNUInWorldDetail.as_view(), name="snu_in_world_detail"),
    path('tag/<int:pk>/', views.TagDetail.as_view(), name="tag_detail"),
    path('schools/', views.SchoolList.as_view(), name="school_list"),
    path('school/', include([
        path('update/<str:topic>/', views.SchoolUpdate.as_view(), name="school_update"),
        path('update/auto/<int:pk>/', views.SchoolAutodataUpdate.as_view(), name="school_autodata_update"),
        path('tag/', views.SchoolTag.as_view(), name="school_tag"),
        path('like/', views.SchoolLike.as_view(), name="school_like"),
        path('rate/', views.SchoolRate.as_view(), name="school_rate"),
        path('search/', views.SchoolSearch.as_view(), name="school_search"),
        path('filter/', views.SchoolFilterSearch.as_view(), name="school_filter_search"),
    ])),
]
