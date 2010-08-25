from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Static files (should served by Apache in prod)
    (r'^static/(.*)$', 'django.views.static.serve', {'document_root': 'static'}),                       
                        
    # User-facing URL matching                       
    (r'^league/', include('butkus.league.urls')),                       
    (r'^ncf/', include('butkus.ncf.urls')),                       
    (r'^personal/', include('butkus.personal.urls')),                       
    (r'^team/', include('butkus.team.urls')),                       

    # Admin site URL matching
    (r'^admin/', include('django.contrib.admin.urls')),

    # Auth URL matching
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    (r'^accounts/profile/$', 'django.contrib.auth.views.profile'),
)
