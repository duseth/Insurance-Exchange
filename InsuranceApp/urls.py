from . import views

from django.urls import path

app_name = "InsuranceApp"

urlpatterns = [
    path("", views.ServiceListView.as_view(), name="index"),
    path("login", views.LoginView.as_view(), name="login"),
    path("register", views.RegisterView.as_view(), name="register"),
    path("logout", views.LogoutView.as_view(), name="logout"),
    path("profile", views.UpdateUserView.as_view(), name="profile"),
    path("services", views.CompanyServicesView.as_view(), name="services"),
    path("create_service", views.CreateServiceView.as_view(), name="create_service"),
    path("update_service/<int:service_id>", views.UpdateServiceView.as_view(), name="update_service"),
    path("delete_service/<int:service_id>", views.DeleteServiceView.as_view(), name="delete_service"),
    path("services/<int:service_id>", views.ServiceView.as_view(), name="service"),
    path("responses", views.ResponsesView.as_view(), name="responses")
]
