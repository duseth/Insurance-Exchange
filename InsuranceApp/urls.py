from django.urls import path
from . import views

app_name = "InsuranceApp"


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.auth, name="login"),
    path("register", views.register, name="register")
]
