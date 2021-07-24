from .models import *
from django import forms
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm):
    name = forms.CharField(max_length=200)
    email = forms.EmailField(max_length=255, widget=forms.EmailInput)
    phone = forms.CharField(max_length=20)
    description = forms.Textarea()

    class Meta:
        model = Company
        fields = ("name", "email", "phone", "description", "password1", "password2")

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
