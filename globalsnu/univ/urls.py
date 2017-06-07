from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^snuinworld/$', views.SNUInWorldList.as_view(), name="snu_in_world"),
    url(r'^snuinworld/(\w+)/$', views.SNUInWorldDetail.as_view(), name="snu_in_world_detail"),
    url(r'^tag/(?P<pk>\d+)/$', views.TagDetail.as_view(), name="tag_detail"),
    url(r'^schools/$', views.SchoolList.as_view(), name="school_list"),
    url(r'^school/', include([
        url(r'^update/(\w+)/$', views.SchoolUpdate.as_view(), name="school_update"),
        url(r'^update/auto/(?P<pk>\d+)/$', views.SchoolAutodataUpdate.as_view(), name="school_autodata_update"),
        url(r'^tag/$', views.SchoolTag.as_view(), name="school_tag"),
        url(r'^like/$', views.SchoolLike.as_view(), name="school_like"),
        url(r'^rate/$', views.SchoolRate.as_view(), name="school_rate"),
        url(r'^search/$', views.SchoolSearch.as_view(), name="school_search"),
        url(r'^filter/$', views.SchoolFilterSearch.as_view(), name="school_filter_search"),
    ])),
]
