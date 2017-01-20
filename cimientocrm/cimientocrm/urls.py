from django.conf.urls import patterns, include, url
from django.conf import settings
from custom.sites import admine
#from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'crm.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),
	url(r'^admin/', include(admine.urls)),
	url(r'^listar/', include('gestor.urls')),
	url(r'^', include('genericdropdown.urls')),
)

if settings.DEBUG:
	urlpatterns += patterns('',
	url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}))
