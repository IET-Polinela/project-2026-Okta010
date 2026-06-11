from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CitizenRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email") # is_admin akan otomatis bernilai False