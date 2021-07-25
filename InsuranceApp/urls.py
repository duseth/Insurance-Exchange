from . import views
from django.urls import path

app_name = "InsuranceApp"


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_user, name="login"),
    path("register", views.register_user, name="register"),
    path("logout", views.logout_user, name="logout"),
    path("profile", views.update_user, name="profile"),
    path("services", views.get_services, name="services"),
    path("create_service", views.create_service, name="create_service"),
    path("update_service/<int:service_id>", views.update_service, name="update_service"),
    path("delete_service/<int:service_id>", views.delete_service, name="delete_service"),
    path("services/<int:service_id>", views.service_response, name="service"),
    path("responses", views.get_responses, name="responses")
]
