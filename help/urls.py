from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^$', views.TT_help_index, name='TT Help Page'),
    url(r'^faq/$', views.TT_help_faq, name='TT Help FAQ Page'),
    url(r'^salute/$', views.TT_help_salute, name='TT Help Salute Page'),
    url(r'^about/$', views.TT_help_about, name='TT Help About Page'),
    url(r'^screenshots/$', views.TT_help_screenshots, name='TT Help Screenshots Page'),
)
