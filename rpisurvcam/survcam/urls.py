from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # TODO: add CSRF token and get rid of the CSRF exemption:
    url(r'^move', views.move, name='move'),
    url(r'^update-status', views.update_status, name='update_status'),
    url(r'^snapshot', views.snapshot, name='snapshot'),
    url(r'^download-motion', views.download_motion, name='download_motion'),
    url(r'^camera-on', views.camera_on, name='camera_on'),
    url(r'^camera-off', views.camera_off, name='camera_off'),
]
