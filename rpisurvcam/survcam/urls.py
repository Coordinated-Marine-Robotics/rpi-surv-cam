from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),    # TODO: FIXME
    url(r'^move', views.move, name='move'),
    url(r'^snapshot', views.snapshot, name='snapshot'),
]
