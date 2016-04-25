from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # TODO: add CSRF token and get rid of the CSRF exemption:
    url(r'^move', views.move, name='move'),
    url(r'^update-target', views.update_target, name='update_target'),
    url(r'^snapshot', views.snapshot, name='snapshot'),
]
