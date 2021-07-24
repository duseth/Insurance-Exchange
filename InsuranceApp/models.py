from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField


class Company(AbstractUser):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=20)
    description = models.TextField(null=True)
    password = models.CharField(max_length=200)
    create_date = models.DateField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "phone", "password"]


class InsuranceType(models.Model):
    name = models.CharField(max_length=200)
    risks = ArrayField(models.CharField(max_length=30))


class ValidityType(models.Model):
    name = models.CharField(max_length=20)
    time = models.FloatField()


class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True)
    type = models.ForeignKey(InsuranceType, on_delete=models.CASCADE)
    insurance_validity = models.ForeignKey(ValidityType, on_delete=models.CASCADE)
    coverage_amount = models.FloatField()
    price = models.FloatField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)


class Response(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20)
    birth_date = models.DateField()
    response_date = models.DateField(auto_now_add=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
