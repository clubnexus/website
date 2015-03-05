from django.conf.urls import patterns, include, url

from users import views as users_views
from help import views as help_views
from news import views as news_views

urlpatterns = patterns('',
    url(r'^$', news_views.home, name='home'),
    url(r'^ckeditor/', include('ckeditor.urls')),
    
    url(r'^play/$', news_views.play, name='play'),
    url(r'^news/', include('news.urls', namespace='news')),
    url(r'^help/', include('help.urls', namespace='help')),
    url(r'^graphapi/', include('api.urls', namespace='api')),
    
    url(r'^login/$', users_views.TT_login, name='TT Login Page'),
    url(r'^logout/$', users_views.TT_logout, name='TT Logout Page'),
    url(r'^register/$', users_views.TT_register, name='TT Register Page'),
    url(r'^register/success/$', users_views.TT_register_success, name='TT Register Success Page'),
    url(r'^register/resend/$', users_views.TT_register_resend, name='TT Register Resend Page'),
    url(r'^verify/(?P<token>\w+)', users_views.TT_verify, name='TT Verify Page'),
    url(r'^forgotpass/$', users_views.TT_forgotpass, name='TT Forgot Password Page'),
    url(r'^resetpass/(?P<token>\w+)', users_views.TT_resetpass, name='TT Forgot Password Page'),
    
    url(r'^account/', include('users.urls', namespace='account'))
)

handler400 = 'users.views.errorpage'
handler403 = 'users.views.errorpage'
handler404 = 'users.views.errorpage'
handler500 = 'users.views.errorpage'
