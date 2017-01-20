from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^updatecombo/(?P<id>\d+)?$', 'genericdropdown.views.updateCombo', name='updatecombo'),
)
