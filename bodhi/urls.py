from django.conf.urls.defaults import *
from bodhi.views import *

urlpatterns = patterns('',
    (r'^$', index),
)
