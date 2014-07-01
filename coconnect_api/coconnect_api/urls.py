from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from mobile import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'coconnect_api.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^coconnect/register/', views.registerUser),
    url(r'^coconnect/profile/', views.userProfile),
    url(r'^coconnect/recordPlace/', views.recordPlace),
    url(r'^coconnect/recordTime/', views.recordTime),
    url(r'^coconnect/proximity/', views.getUsersInProximity),
)
