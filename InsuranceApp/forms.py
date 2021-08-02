from django import forms
from datetime import date
from django.contrib.auth.forms import UserCreationForm

from .models import Company, Service, Response, ValidityType, InsuranceType


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


class UpdateUserForm(forms.ModelForm):
    name = forms.CharField(max_length=200)
    email = forms.EmailField(max_length=255, widget=forms.EmailInput, disabled=True)
    phone = forms.CharField(max_length=20)
    description = forms.Textarea()

    class Meta:
        model = Company
        fields = ("name", "email", "phone", "description")


class ServiceForm(forms.ModelForm):
    title = forms.CharField(max_length=200)
    price = forms.FloatField()
    coverage_amount = forms.FloatField()
    description = forms.Textarea()
    type = forms.ChoiceField(widget=forms.Select, choices=InsuranceType.objects.all().values_list("pk", "name"))
    validity = forms.ChoiceField(widget=forms.Select, choices=ValidityType.objects.all().values_list("pk", "name"))

    class Meta:
        model = Service
        fields = ("title", "description", "coverage_amount", "price", "type", "validity")

    def clean_type(self):
        return InsuranceType.objects.get(pk=self.cleaned_data["type"])

    def clean_validity(self):
        return ValidityType.objects.get(pk=self.cleaned_data["validity"])


class ResponseForm(forms.ModelForm):
    full_name = forms.CharField(max_length=200)
    email = forms.EmailField(widget=forms.EmailInput, max_length=200)
    phone = forms.CharField(max_length=12)
    birth_date = forms.DateField(initial=date.today())

    class Meta:
        model = Response
        fields = ("full_name", "email", "phone", "birth_date")
