from django.conf.urls import patterns, include, url
from django.contrib import admin

import views

urlpatterns = patterns('',
    url(r'^invasions/', views.TT_api_invasions, name='TT Graph API Invasions'),
)

admin.autodiscover()
