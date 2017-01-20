from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_save

class MyAppConfig(AppConfig):
	name = 'gestor'
	verbose_name = 'Mi Gestor'
    
	def ready(self):
		from .signals import create_profile_handler
		post_save.connect(
			receiver = create_profile_handler,
			sender = settings.AUTH_USER_MODEL
		)

		from .signals import chequear_tratamiento_completo
		from .models import Turno
		post_save.connect(
			receiver = chequear_tratamiento_completo,
			sender = Turno
		)

		from .signals import create_company_group
		from .models import Company
		post_save.connect(
			receiver = create_company_group,
			sender = Company
		)
