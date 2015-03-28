from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^login/$', views.login, name='login')
)
