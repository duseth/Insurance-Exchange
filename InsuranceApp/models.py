from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField


class Company(AbstractUser):
    """Users within the Django authentication system are represented by this model"""
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=20)
    description = models.TextField(null=True)
    password = models.CharField(max_length=200)
    create_date = models.DateField(auto_now_add=True)
    username = models.CharField(max_length=30, unique=False)

    # Overridden attribute for Django authentication system, because 'username' field does not exist
    USERNAME_FIELD = "email"

    # Overridden attribute to avoid collisions with 'USERNAME_FIELD'
    REQUIRED_FIELDS = ["name", "phone", "password"]


class InsuranceType(models.Model):
    """Insurance type model that represent 'name' and 'risks' of insurance"""
    name = models.CharField(max_length=200)
    risks = ArrayField(models.CharField(max_length=30))


class ValidityType(models.Model):
    """Validity type model that represent 'name' and 'time' of insurance"""
    name = models.CharField(max_length=20)
    time = models.FloatField()


class Service(models.Model):
    """Service model for represent service by 'company'"""
    title = models.CharField(max_length=200)
    description = models.TextField(null=True)
    type = models.ForeignKey(InsuranceType, on_delete=models.CASCADE)
    validity = models.ForeignKey(ValidityType, on_delete=models.CASCADE)
    coverage_amount = models.FloatField()
    price = models.FloatField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)


class Response(models.Model):
    """Response model for represent response by client for 'company'"""
    full_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20)
    birth_date = models.DateField()
    response_date = models.DateField(auto_now_add=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
