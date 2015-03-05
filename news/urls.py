from django.conf.urls import patterns, include, url
from django.contrib import admin

import views

urlpatterns = patterns('',
    url(r'^$', views.news, name='news'),
    url(r'^make/$', views.make, name='make'),
    url(r'^comment/(?P<post_id>\w+)/$', views.comment, name='comment'),
    url(r'^post/(?P<post_id>\w+)/$', views.detail, name='detail'),
    url(r'^review/$', views.review, name='review')
)
