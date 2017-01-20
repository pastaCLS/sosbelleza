from django.forms import ModelForm
from image_cropping import ImageCropWidget
from .models import Customer, Profile, Company

class CustomerForm(ModelForm):
	class Meta:
		model = Customer
		fields = ("name", "birthdate", "phone", "email", "facebook", "whatsapp", "photo", "cropping", "communication", "source", "referer")
		widgets = {
			"photo": ImageCropWidget(),
		}

class ProfileForm(ModelForm):
	class Meta:
		model = Profile
		fields = ("photo", "cropping")
		widgets = {
			"photo": ImageCropWidget(),
		}

class CompanyForm(ModelForm):
	class Meta:
		model = Company
		fields = ("name", "cuit", "logo",)
