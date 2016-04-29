from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # TODO: add CSRF token and get rid of the CSRF exemption:
    url(r'^move', views.move, name='move'),
    url(r'^update-status', views.update_status, name='update_status'),
    url(r'^snapshot', views.snapshot, name='snapshot'),
]
