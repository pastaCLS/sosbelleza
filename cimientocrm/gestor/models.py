# -*- encoding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from image_cropping import ImageRatioField, ImageCropField
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

import os

#Tratamientos
class Machine(models.Model):
	owner = models.ForeignKey(settings.AUTH_USER_MODEL)
	name = models.CharField('Nombre de la maquina', max_length=25)
	availability = models.PositiveIntegerField('Cantidad disponible')
	def __str__(self):
		return "{}".format(self.name)
	class Meta:
		verbose_name = "maquina"

class BaseTreatment(models.Model):
	TREATMENT_TYPES = (
		(0, 'Con maquinas'),
		(1, 'Sin maquinas')
	)
	name = models.CharField('Nombre', max_length=25)
	description = models.CharField('Descripción', max_length=1200)
	treatment_type = models.IntegerField('Tipo de tratamiento', null=True, choices=TREATMENT_TYPES)
	time_needed = models.DurationField('Duración del turno')
	class Meta:
		abstract = True

class MachineTreatment(models.Model):
	machine_used = models.ForeignKey(Machine)
	class Meta:
		abstract = True

class ByHandTreatment(models.Model):
	owner = models.ForeignKey(settings.AUTH_USER_MODEL)
	class Meta:
		abstract = True

class Treatment(ByHandTreatment, MachineTreatment, BaseTreatment):
	pass

	def __str__(self):
		return "{}".format(self.name)

	class Meta:
		verbose_name = "tratamiento"

#Gabinetes, Locales y Empresa
def logo_dir(instance, filename):
	return os.path.join("company-{0}".format(instance.name.replace(" ", "-")), filename)

class Company(models.Model):
	owner = models.ForeignKey(settings.AUTH_USER_MODEL)
	name = models.CharField("Nombre de la empresa", max_length=35, blank=True)
	cuit = models.PositiveIntegerField('CUIT', blank=True)
	loading_date = models.DateField(auto_now=True)
	logo = models.ImageField(upload_to = logo_dir)

	def __str__(self):
		return "{0}".format(self.name)

	class Meta:
		verbose_name = "empresa"

class Branch(models.Model):
	owner = models.ForeignKey(Company)

	street = models.CharField("calle", max_length=30)
	number = models.PositiveIntegerField("numero")
	flat = models.PositiveIntegerField("piso", default=0)
	department = models.CharField("depto.", max_length=2, null=True)
	postcode = models.PositiveIntegerField("codigo postal")

	def __str__(self):
		return "{} {} {}-{}".format(self.street, self.number, self.flat, self.department)

	class Meta:
		verbose_name = "local"
		verbose_name_plural = "locales"

class Cabinet(models.Model):
	branch = models.ForeignKey(Branch, verbose_name="local")
	number = models.PositiveIntegerField("Numero", help_text='Identificador para el gabinete')
	treatments = models.ManyToManyField(Treatment, verbose_name="tratamientos disponibles", help_text="tener en cuenta disponibilidad de maquinas")

	def __str__(self):
		return "Gabinete {} en local {}".format(self.number, self.branch)	
	
	class Meta:
		verbose_name = "gabinete"
		verbose_name_plural = "gabinetes"

#Clientes
def customer_dir(instance, filename):
	return os.path.join("company-{0}".format(instance.loaded_by.name.replace(" ", "-")), filename)

class Customer(models.Model):
	WHATSAPP = "WA"
	FACEBOOK = "FB"
	EMAIL = "EM"

	COMMUNICATION_CHOICES = (
		(WHATSAPP, "Mensaje de WhatsApp"),
		(FACEBOOK, "Mensaje de Facebook"),
		(EMAIL, "Email"),
	)

	REFERIDO = "RE"
	PUBLI_CLASSIC = "CL"
	PUBLI_INET = "IN"
	OTRO = "OT"

	SOURCE_CHOICES = (
		(REFERIDO, "Por otra clienta"),
		(FACEBOOK, "Facebook Inc."),
		(PUBLI_CLASSIC, "Folleto y graficas"),
		(PUBLI_INET, "Publicidad en internet"),
		(OTRO, "Otro"),
	)

	FEMENINO = "MA"
	MASCULINO = "FE"
	OTRO = "OT"

	GENDER_CHOICES = (
		(FEMENINO, "Femenino"),
		(MASCULINO, "Masculino"),
		(OTRO, "Otro"),
	)

	name = models.CharField("Nombre", max_length=35)
	birthdate = models.DateField("Fecha de cumpleaños")

	owner = models.ForeignKey(settings.AUTH_USER_MODEL)

	phone = models.CharField("Telefono", max_length=16, blank=True)
	email = models.EmailField(blank=True)
	facebook = models.CharField(max_length=22, help_text="sin la url facebook.com", blank=True)
	whatsapp = models.BooleanField()

	communication = models.CharField("Medio de comunicación", max_length=2, choices=COMMUNICATION_CHOICES, blank=True)
	source = models.CharField("¿Como nos conociste?", max_length=2, choices=SOURCE_CHOICES)
	referer = models.ForeignKey("self", blank=True, null=True)

	photo = ImageCropField("Foto", upload_to=customer_dir)
	cropping = ImageRatioField('photo', '200x200')

	date = models.DateField(auto_now=True)
	gender = models.CharField(max_length=2, choices=GENDER_CHOICES)
	def thumbnail(self):
		return """<img border="0" alt="" src="/media/%s" height="40" />""" % (self.photo.name)
	thumbnail.allow_tags = True


	@property
	def age(self):
		today = datetime.date.today()
		return (today.year - self.birthdate.year) - int((today.month, today.day) < (self.birthdate.month, self.birthdate.day))

	def __str__(self):
		return "{0}".format(self.name)

	class Meta:
		verbose_name = "cliente"
		#verbose_name_plural = "clientes"

#Sesiones
class Session(models.Model):
	owner = models.ForeignKey(settings.AUTH_USER_MODEL)
	treatment = models.ForeignKey(Treatment)
	customer = models.ForeignKey(Customer)
	number_of_sessions = models.PositiveIntegerField('Cantidad de sesiones')
	price_total = models.FloatField('Precio total')
	price_cashed = models.FloatField('Precio pagado')
	date = models.DateField(auto_now=True)
	complete = models.BooleanField('Completado', default=False)

	def __str__(self):
		return "{} de {}".format(self.treatment.name, self.customer.name)

	class Meta:
		verbose_name = "sesion"
		verbose_name_plural = "sesiones"

#Turnos
class Turno(models.Model):
	owner = models.ForeignKey(settings.AUTH_USER_MODEL)

	date = models.DateTimeField("Fecha y hora")
	cabinet_used = models.ForeignKey(Cabinet, verbose_name="gabinete")
	limit = models.Q(app_label="gestor", model="comboasignado") | models.Q(app_label="gestor", model="session")
	content_type = models.ForeignKey(ContentType, limit_choices_to=limit)
	object_id = models.PositiveIntegerField()
	content_object = generic.GenericForeignKey('content_type', 'object_id')
	canceled = models.BooleanField('Cancelado', default=False)
	perdido = models.BooleanField(default=False)

	def __str__(self):
		return "el {} en gabinete {}".format(self.date.strftime("%d-%m-%Y %H:%M"), self.cabinet_used)
	
	class Meta:
		verbose_name = "turno"
		ordering = ['date',]

#Perfiles
def staff_directory(instance, filename):
	return os.path.join("company-{}".format(instance.user.company.name.replace(" ", "-")), "staff", filename)

class Profile(models.Model):
	FREE = "FR"
	PLATINUM = "PL"
	GOLD = "GL"
	ENTERPRISE = "EN"

	PLAN_CHOICES = (
		(FREE, "Gratis, 5 clientes 1 administrador"),
		(PLATINUM, "50 clientes, 2 administradores"),
		(GOLD, "250 clientes, 5 administradores"),
		(ENTERPRISE, "clientes y administradores ilimitados")
	)

	user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
	plan = models.CharField(max_length=2, choices=PLAN_CHOICES)
	photo = models.ImageField("Foto de perfil", upload_to=staff_directory)

	cropping = ImageRatioField('photo', '200x200')

	def __str__(self):
		return "{}".format(self.user.username)

	class Meta:
		verbose_name = "perfil"
		verbose_name_plural = "perfiles"
	
class Provider(models.Model):
	owner = models.ForeignKey(settings.AUTH_USER_MODEL)
	name = models.CharField('Nombre de fantasia', max_length=30)
	cuit = models.PositiveIntegerField('CUIT')

	street = models.CharField("calle", max_length=30)
	number = models.PositiveIntegerField("numero")
	flat = models.PositiveIntegerField("piso", default=0)
	department = models.CharField("depto.", max_length=2, null=True)
	postcode = models.PositiveIntegerField("codigo postal")

	phone = models.CharField('Telefono', max_length=25)
	mail = models.EmailField('email')
	bank_account = models.CharField('Cuenta', max_length=30, null=True, blank=True)

	def __str__(self):
		return "{}".format(self.name)

	class Meta:
		verbose_name = "proveedor"
		verbose_name_plural = "proveedores"


def product_dir(instance, filename):
	return os.path.join("company-{0}".format(instance.user.company.name.replace(" ", "-")), "products", filename)

class Product(models.Model):
	CENTIMETRO = "cc"
	MILILITRO = "ml"
	LITRO = "lt"
	KILO = "kg"
	GRAMO = "gr"
	
	SUFFIX_CHOICES = (
		(CENTIMETRO, "centimetros cubicos"),
		(MILILITRO, "mililitros"),
		(LITRO, "litro"),
		(KILO, "kilogramo"),
		(GRAMO, "gramo"),
	)

	owner = models.ForeignKey(settings.AUTH_USER_MODEL)
	provider = models.ForeignKey(Provider)

	product = models.CharField('Producto', max_length=35)
	sku = models.PositiveIntegerField('Codigo de barras')
	price = models.FloatField('Precio')
	porcentaje = models.PositiveIntegerField('Porcentaje de ganancia')
	quantity = models.PositiveIntegerField('Cantidad')
	
	
	presentation = models.PositiveIntegerField('presentacion')
	presentation_suffix = models.CharField('medida', max_length = 2, choices = SUFFIX_CHOICES)
	description = models.TextField('descripción')

	image = models.ImageField('Foto', upload_to = product_dir)
	cropping = ImageRatioField('image', '200x200')

	def __str__(self):
		return "{} de {} {}".format(self.product, self.presentation, self.presentation_suffix)

	class Meta:
		verbose_name = "producto"
		verbose_name_plural = "productos"
	
class Sale(models.Model):
	owner = models.ForeignKey(settings.AUTH_USER_MODEL)
	products = models.ManyToManyField(Product)
	cashed = models.FloatField('Cobrado')
	date = models.DateTimeField(auto_now = True)
	
	class Meta:
		verbose_name = "venta"
		verbose_name_plural = "ventas"

class AdminProfile(models.Model):
	owner = models.OneToOneField(settings.AUTH_USER_MODEL)
	image = models.ImageField(upload_to="staff")
	def __str__(self):
		return "Perfil administrativo de {}".format(self.user.username)

class Tip(models.Model):
	admin = models.ForeignKey(AdminProfile)
	message = models.CharField(max_length=200)
	url = models.URLField()
	def __str__(self):
		return "{}".format(self.message)

class Combo(models.Model):
	owner = models.ForeignKey(settings.AUTH_USER_MODEL)
	nombre = models.CharField(max_length=35)
	tratamientos = models.ManyToManyField(Treatment, through='ComboTratamiento')
	def __str__(self):
		return "{}".format(self.nombre)

class ComboTratamiento(models.Model):
	owner = models.ForeignKey(settings.AUTH_USER_MODEL)
	combo = models.ForeignKey(Combo)
	tratamiento = models.ForeignKey(Treatment)
	cantidad = models.PositiveIntegerField()

class ComboAsignado(models.Model):
	owner = models.ForeignKey(settings.AUTH_USER_MODEL)
	customer = models.ForeignKey(Customer)
	combo = models.ForeignKey(Combo)
	asignado = models.DateField(auto_now=True)
	complete = models.BooleanField('Completado', default=False)
	def __str__(self):
		return "{} {}".format(self.combo.nombre, self.customer.name)

def seguimiento_dir(instance, filename):
	return os.path.join("company-{0}".format(instance.owner.name.replace(" ", "-")), "seguimiento", instance.customer.name, filename)

class Seguimiento(models.Model):
	owner = models.ForeignKey(settings.AUTH_USER_MODEL)
	customer = models.ForeignKey(Customer)
	photo = models.ImageField('Foto', upload_to = seguimiento_dir)
	date = models.DateField('Fecha')
