from django import forms
from datetime import date
from django.contrib.auth.forms import UserCreationForm

from .models import Company, Service, Response, ValidityType, InsuranceType


class RegisterForm(UserCreationForm):
    """A form that creates a user, with no privileges, from the given username and password"""
    name = forms.CharField(max_length=200)
    email = forms.EmailField(max_length=255, widget=forms.EmailInput)
    phone = forms.CharField(max_length=20)
    description = forms.Textarea()

    class Meta:
        """Configuration class for auto-generated fields and form customizations"""
        model = Company
        fields = ("name", "email", "phone", "description", "password1", "password2")

    def save(self, commit=True):
        """Save this form's self.instance object if commit=True. Otherwise, add
        a email fields to the model and save. Return the model instance."""
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class UpdateUserForm(forms.ModelForm):
    """A form that updates existing user"""
    name = forms.CharField(max_length=200)
    email = forms.EmailField(max_length=255, widget=forms.EmailInput, disabled=True)
    phone = forms.CharField(max_length=20)
    description = forms.Textarea()

    class Meta:
        """Configuration class for auto-generated fields and form customizations"""
        model = Company
        fields = ("name", "email", "phone", "description")


class ServiceForm(forms.ModelForm):
    """A form that create and update service object"""
    title = forms.CharField(max_length=200)
    price = forms.FloatField()
    coverage_amount = forms.FloatField()
    description = forms.Textarea()
    type = forms.ChoiceField(widget=forms.Select, choices=InsuranceType.objects.values_list("pk", "name"))
    validity = forms.ChoiceField(widget=forms.Select, choices=ValidityType.objects.values_list("pk", "name"))

    class Meta:
        """Configuration class for auto-generated fields and form customizations"""
        model = Service
        fields = ("title", "description", "coverage_amount", "price", "type", "validity")

    def clean_type(self):
        """Method for cleaning data from 'type' field. Return 'InsuranceType' object by primary key."""
        return InsuranceType.objects.get(pk=self.cleaned_data["type"])

    def clean_validity(self):
        """Method for cleaning data from 'validity' field. Return 'ValidityType' object by primary key."""
        return ValidityType.objects.get(pk=self.cleaned_data["validity"])


class ResponseForm(forms.ModelForm):
    """A form that create response object"""
    full_name = forms.CharField(max_length=200)
    email = forms.EmailField(widget=forms.EmailInput, max_length=200)
    phone = forms.CharField(max_length=12)
    birth_date = forms.DateField(initial=date.today())

    class Meta:
        """Configuration class for auto-generated fields and form customizations"""
        model = Response
        fields = ("full_name", "email", "phone", "birth_date")
