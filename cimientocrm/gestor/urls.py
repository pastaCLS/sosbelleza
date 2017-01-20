from django.conf.urls import url
from .views import ProductList, ProductListJSON, ConfigOneShoot, OnSuccessCompany

#cambiar, esto tiene que pasar a ser por compania
urlpatterns = [
	url(r'^productos/(?P<pk>\d+)$', ProductList.as_view()),
	url(r'^productos/json/(?P<empresa_pk>\d+)$', ProductListJSON),
	url(r'^configurar/empresa$', ConfigOneShoot.as_view(), name="config_one_shoot"),
	url(r'^gracias$', OnSuccessCompany.as_view(), name="thanks"),
]
