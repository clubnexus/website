from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^login/$', views.PAPI_login, name='login')
)
