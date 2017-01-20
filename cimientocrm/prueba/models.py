from django.db import models

class Prueba(models.Model):
	nombre = models.CharField(max_length=10)
	apellido = models.CharField(max_length=10)
	edad = models.IntegerField()

	def __str__(self):
		return "{0}".format(self.nombre)

class Nuevo(models.Model):
	telefono = models.CharField(max_length=20)
	computadora = models.CharField(max_length=20)

	def __str__(self):
		return "{0}".format(self.telefono)
