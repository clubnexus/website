from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^login/$', views.PAPI_login, name='login'),
    url(r'^ban/$', views.PAPI_ban, name='ban'),
    url(r'^names/$', views.PAPI_names, name='ban'),
    url(r'^cookie/$', views.PAPI_cookie, name='cookie'),
)
