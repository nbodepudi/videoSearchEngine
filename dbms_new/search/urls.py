from django.conf.urls import include, url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^search/',views.index,name = 'index'),
    url(r'^login/$', auth_views.login, {'template_name': 'start/login.html'}, name='login'),
    url(r'^logout/$',auth_views.logout,{'template_name': 'start/logged_out.html'}, name='logout'),
    url(r'^signup/',views.signup,name='signup'),
    url(r'^home/$', auth_views.login, {'template_name': 'start/home.html'}, name='login')
]
