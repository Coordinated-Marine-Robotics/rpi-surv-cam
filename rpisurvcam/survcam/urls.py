from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # TODO: add CSRF token and get rid of the CSRF exemption:
    url(r'^move', csrf_exempt(views.MoveView.as_view(), name='move'),
    url(r'^snapshot', views.snapshot, name='snapshot'),
]
