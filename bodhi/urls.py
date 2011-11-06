from django.conf.urls.defaults import *

urlpatterns = patterns('bodhi.views',
    (r'^$', 'index'),
    (r'^(\d+)/$', 'device'),
    (r'^(\d+)/ping$', 'device_ping'),
    (r'^(\d+)/wol$', 'device_wol'),
    (r'^(\d+)/pass$', 'device_ask_pass'),
    (r'^(\d+)/shutdown$', 'device_shutdown'),
    (r'^(\d+)/reboot$', 'device_shutdown'),
    (r'^(\d+)/img/(\d{1,2})$', 'history_image'),
)
