def create_profile_handler(sender, instance, created, **kwargs):
	from .models import Company, Profile
	if not created:
		return

	if not instance.is_superuser:
		profile = Profile(user = instance)
		profile.save()

def chequear_tratamiento_completo(sender, instance, created, **kwargs):
	from django.contrib.contenttypes.models import ContentType
	from .models import Turno, Session, ComboAsignado
	if type(instance.content_object) is Session:
		totales = instance.content_object.number_of_sessions
		anteriores = Turno.objects.filter(content_type=ContentType.objects.get_for_model(Session), canceled=False, object_id=instance.object_id).count()
		print "%d - %d" % (totales, anteriores)
		if totales == anteriores:
			sesion = Session.objects.get(pk = instance.object_id)
			sesion.complete = True
			sesion.save()
	else:
		totales = instance.content_object.combo.tratamientos.through.objects.all().values('cantidad')
		anteriores = Turno.objects.filter(content_type=ContentType.objects.get_for_model(ComboAsignado), canceled=False, object_id=instance.object_id).count()
		if totales == anteriores:
			combo = ComboAsignado.objects.filter(pk = instance.object_id)
			combo.complete = True
			combo.save()

def create_company_group(sender, instance, created, **kwargs):
	from .models import Company
	if not created:
		return
	Group.objects.create(name=instance.name)
