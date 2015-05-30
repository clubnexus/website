from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^post/', views.post, name='post'),
)

handler400 = 'users.views.errorpage'
handler403 = 'users.views.errorpage'
handler404 = 'users.views.errorpage'
handler500 = 'users.views.errorpage'
