from django.contrib import admin
from custom.sites import admine
from models import Prueba, Nuevo

class NuevoAdmin(admin.ModelAdmin):
	pass

admine.register(Nuevo, NuevoAdmin)

class PruebaAdmin(admin.ModelAdmin):
	pass

admine.register(Prueba, PruebaAdmin)
