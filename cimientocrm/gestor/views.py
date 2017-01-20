from django.views.generic import ListView, FormView, TemplateView
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core import serializers
from django.core.urlresolvers import reverse_lazy
from .forms import CompanyForm

from .models import Product

class OnSuccessCompany(TemplateView):
	template_name = "changeform_on_success_company.html"

class ConfigOneShoot(FormView):
	form_class = CompanyForm
	success_url = reverse_lazy("thanks")
	template_name = "changeform_company.html"

class ThanksForLoadCompany(TemplateView):
	pass

class ProductList(ListView):
	model = Product
	def get_queryset(self):
		qs = Product.objects.filter(user = User.objects.get(pk = self.kwargs.get("pk")))
		return qs

def ProductListJSON(request, empresa_pk):
	products = Product.objects.filter(user = User.objects.get(pk = empresa_pk))
	return HttpResponse(serializers.serialize("json", products ))
