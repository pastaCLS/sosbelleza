from django.contrib import admin
from custom.sites import admine
from image_cropping import ImageCroppingMixin

from datetime import date
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.admin import DateFieldListFilter, SimpleListFilter
from import_export import resources
from import_export.admin import ImportExportMixin

from .models import Company, Branch, Cabinet, Profile, Customer, Treatment, Machine, Session, Turno
from .models import Sale, Product, Provider, Combo, ComboAsignado, Seguimiento#, TurnoCombo

from .forms import CustomerForm, ProfileForm

import os

class FilteredModelAdmin(admin.ModelAdmin):
	exclude = ('owner',)

	def save_model(self, request, obj, form, change):
		if not change:
			obj.user = request.user
		obj.save()

	def get_queryset(self, request):
		qs = super(FilteredModelAdmin, self).get_queryset(request)
		if request.user.is_superuser:
			return qs
		return qs.filter(user = request.user)	

class SaleAdmin(FilteredModelAdmin):
	pass	

def precio_final(obj):
	return "%.2f" % ((obj.price * (1 + obj.porcentaje/100.0)))
precio_final.short_description = "Precio a cliente"

class ProductAdmin(FilteredModelAdmin):
	list_display = ('product', 'quantity', 'description', precio_final)
	
class ProviderAdmin(FilteredModelAdmin):
	pass

class CabinetAdmin(FilteredModelAdmin):
	pass

class CustomerWithSessions(SimpleListFilter):
	title = 'sesion'
	# parametro es el dato que se envia por URL
	parameter_name = 'name'

	def lookups(self, request, model_admin):
		# esta tupla muestra las opciones, la segunda
		# es el nombre que aparece y la primera el valor
		# del parameter_name.
		return (
			('fruta', 'Sesion activa'),
			('combo', 'Combo activo'),
		)

	def queryset(self, request, queryset):
		# aca nos cae el valor de la opcion elegida.
		if self.value() == 'fruta':
			return Customer.objects.filter(pk__in = Session.objects.filter(owner = request.user.company).values('customer'))
		elif self.value() == 'combo':
			return Customer.objects.filter(pk__in = ComboAsignado.objects.all().values('customer'))

class CustomerResource(resources.ModelResource):
	def before_import(self, dataset, dry_run, *args, **kwargs):
		li = []
		for i in range(0, len(dataset)):
			li.append(User.objects.get(username = kwargs.get('user')).company.id)

		dataset.insert_col(3, li, 'loaded_by')
		print dataset

		return super(CustomerResource, self).before_import(dataset, dry_run, *args, **kwargs)

	class Meta:
		model = Customer
		fields = ('id','name','birthdate','loaded_by', 'phone','email','facebook','whatsapp','communication')

def get_actions(obj):
	return format_html("""
<div class='btn-group'>
  <a data-toggle='tooltip' title='Asignar sesion' href='/admin/gestor/session/add/?customer={0}' class='btn btn-default btn-xs'>Sesion <span class='glyphicon glyphicon-hdd'></span></a>
  <a data-toggle='tooltip' title='Asignar combo' href='/admin/gestor/comboasignado/add?customer={0}' class='btn btn-default btn-xs'>Combo <span class='glyphicon glyphicon-tasks'></span></a>
</div>""".format(obj.pk))

get_actions.short_description = "Asignar"

def view_evolution(obj):
	return format_html('<a href="/admin/gestor/seguimiento/add/?customer=%d" class="btn btn-default btn-xs">Seguimiento</a>' % obj.pk)
view_evolution.short_description = "Administrar"

class CustomerAdmin(ImportExportMixin, ImageCroppingMixin, FilteredModelAdmin):
	exclude = ('loaded_by',)
	list_display = ('thumbnail', 'name', 'phone', get_actions, view_evolution)
	form = CustomerForm
	search_fields = ('name',)
	list_filter = (CustomerWithSessions,)
	resource_class = CustomerResource
	change_list_template = 'change_list_import_export.html'
	export_template_name = 'export.html'
	import_template_name = 'import.html'

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "referer":
			kwargs["queryset"] = Customer.objects.filter(loaded_by=request.user.company)
		return super(CustomerAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class BranchNestedInline(admin.StackedInline):
	model = Branch
	extra = 0

class CompanyAdmin(FilteredModelAdmin):
	inlines = [BranchNestedInline]
	class Media:
		css = {
			"all": (os.path.join("css", "company.css"),)
		}


class ProfileAdmin(FilteredModelAdmin):
	form = ProfileForm

class TreatmentAdmin(FilteredModelAdmin):
	pass

class MachineAdmin(FilteredModelAdmin):
	pass

def get_user(obj):
	return obj.content_object.customer
get_user.short_description = "Cliente"

def get_session(obj):
	if type(obj.content_object) is Session:
		totales = obj.content_object.number_of_sessions
		anteriores = list(Turno.objects.filter(content_type=ContentType.objects.get_for_model(Session), canceled=False, object_id=obj.object_id).order_by('-date'))[::-1].index(obj)
		return "[%d de %d %s]" % (anteriores+1, totales, obj.content_object.treatment.name)
	else:
		totales = obj.content_object.combo.tratamientos.through.objects.all().values('tratamiento__name', 'cantidad')
		anteriores = list(Turno.objects.filter(content_type=ContentType.objects.get_for_model(ComboAsignado), canceled=False, object_id=obj.object_id).order_by('-date'))[::-1].index(obj)

		array = []
		for cnt in totales:
			if anteriores < cnt["cantidad"]:
				array.append("[%d de %d %s] " % (anteriores+1, cnt["cantidad"], cnt["tratamiento__name"]))
		return "{}".format(",".join(array))
		
get_session.short_description = "Sesion"

def get_packet(obj):
	if type(obj.content_object) is Session:
		return "<Sesiones: {1} de {0}>".format(obj.content_object.treatment, obj.content_object.number_of_sessions)
	else:
		return "<Combo: {}>".format(obj.content_object.combo.nombre)
get_packet.short_description = "Paquete contratado"

class TurnoAdmin(FilteredModelAdmin):
	list_display = ('date', get_user, get_session, get_packet)
	list_filter = (
		('date', DateFieldListFilter),
	)

class SessionAdmin(FilteredModelAdmin):
	pass

class ComboTratamientoInline(admin.TabularInline):
	model = Combo.tratamientos.through

class ComboAdmin(FilteredModelAdmin):
	inlines = [
		ComboTratamientoInline,
	]

class SeguimientoAdmin(FilteredModelAdmin):
	pass

class ComboAsignadoAdmin(FilteredModelAdmin):
	pass

admine.register(Seguimiento, SeguimientoAdmin)
admine.register(ComboAsignado, ComboAsignadoAdmin)
admine.register(Combo, ComboAdmin)

admine.register(User, UserAdmin)
admine.register(Group, GroupAdmin)

#admine.register(TurnoCombo, TurnoComboAdmin)
admine.register(Customer, CustomerAdmin)
admine.register(Company, CompanyAdmin)
admine.register(Profile, ProfileAdmin)
admine.register(Treatment, TreatmentAdmin)
admine.register(Machine, MachineAdmin)
admine.register(Turno, TurnoAdmin)
admine.register(Session, SessionAdmin)
admine.register(Cabinet, CabinetAdmin)
admine.register(Provider, ProviderAdmin)
admine.register(Sale, SaleAdmin)
admine.register(Product, ProductAdmin)
