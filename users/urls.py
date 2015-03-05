from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^$', views.TT_account_main, name='TT Account Main'),
    url(r'^events/', views.TT_account_events, name='TT Account Events'),
    url(r'^changepassword/$', views.TT_account_changepassword, name='TT Account Change Password')
)
