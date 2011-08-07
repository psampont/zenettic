from django.conf.urls.defaults import *
from settings import DEBUG

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^bodhi/', include('zenettic.bodhi.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

if DEBUG:
    urlpatterns += patterns('',
        (r'^styles/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': 'c:/Users/psa/Projects/zenettic/templates/styles/'}),
#         {'document_root': '/home/psa/Projects/zenettic/templates/styles/'}),
        (r'^pix/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': 'c:/Users/psa/Projects/zenettic/templates/pix/'}),
#         {'document_root': '/home/psa/Projects/zenettic/templates/pix/'}),
    )

