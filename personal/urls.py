from django.conf.urls.defaults import *

urlpatterns = patterns('butkus.profile.views',
    (r'^$', 'index'),
    (r'^index/$', 'index'),
    (r'^profile/(?P<username>[a-zA-Z]+)/$', 'profile'),
)
