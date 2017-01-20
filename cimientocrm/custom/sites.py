from django.utils.translation import ugettext as _, ugettext_lazy
from django.core.urlresolvers import NoReverseMatch, reverse, reverse_lazy
from django.contrib.admin.sites import AdminSite
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist

from gestor.models import Treatment, Session, Turno, Sale, Company
from datetime import date

import os
import calendar

def days_in_month(year=date.today().year, month=date.today().month):
	return calendar.monthrange(year, month)[1]

class CustomAdmin(AdminSite):
	# URL for the "View site" link at the top ef each admin page.
	index_template = "index.html"
	app_index_template = "app_index.html"
	#login_template = "login.html"
	logout_template = "logout.html"
	password_change_template = "change_password.html"
	password_change_done_template = "change_password_done.html"

	@never_cache
	def index(self, request, extra_context=None):
		# los administradores son marcados como staff
		# y son los duenos de Company
		if request.user.is_staff:
			try:
				empresa = Company.objects.get(owner=request.user)
			except ObjectDoesNotExist:
				return HttpResponseRedirect(reverse_lazy("config_one_shoot"))
		if request.user.is_superuser:
			return super(CustomAdmin, self).index(request, extra_context)
		extra_context = {}
		sesion = []
		for tratamiento in Treatment.objects.filter(owner = request.user):
			sesion.append({
				'name': tratamiento.name,
				'count': Session.objects.filter(owner = request.user.company, treatment = tratamiento).count(),
			})

		# crashea si no tienen nada. verificar
		try:
			Company.objects.get(owner = request.user)
		except DoesNotExist:
			pass
		extra_context["cobrado"] = 10 #Session.objects.filter(owner=request.user.company).aggregate(Sum('price_total')).get('price_total__sum', 0)
		#extra_context["cobrado"] += Sale.objects.filter(user = request.user).aggregate(Sum('cashed')).get('cashed__sum')

		extra_context["sessions"] = sesion
		extra_context["days"] = [Turno.objects.filter(owner = request.user, date__day = str(i)).count() for i in range(0, days_in_month())]

		return super(CustomAdmin, self).index(request, extra_context)

	def each_context(self, request, *args, **kwargs):
		"""
		Returns a dictionary of variables to put in the template context ffor
		*every* page in the admin site.
		"""
		models = []
		context = super(CustomAdmin, self).each_context(request, *args, **kwargs)
		
		"""
		This hook modify the context of the admin page, to access models registered.
		It's for make the menu in the custom templates

		KAKERRR
		"""
		if request.user.is_authenticated():
			for model, model_admin in self._registry.items():
				app_label = model._meta.app_label
				has_module_perms = model_admin.has_module_permission(request)

				if has_module_perms:
					perms = model_admin.get_model_perms(request)

					if True in perms.values():
						registered = {
							'name': (model._meta.verbose_name_plural),
							'object_name': model._meta.object_name,
						}
						info = (model._meta.app_label, model._meta.model_name)
						if perms.get('change', False):
							try:
								registered['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
							except NoReverseMatch:
								pass
						if perms.get('add', False):
							try:
								registered['add_url'] = reverse('admin:%s_%s_add' % info, current_app=self.name)
							except NoReverseMatch:
								pass
						models.append(registered)
	
			models.sort(key=lambda x: x['name'].lower())
			context["registered"] = models

			if request.user.is_superuser:
				context["company_title"] = settings.COMPANY
			else:
				context["company_title"] = request.user.company.name
				context["company_logo"] = request.user.company.logo

		return context

admine = CustomAdmin()
