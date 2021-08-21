from .tasks import send_response_notification
from .services import search_by_services, get_services_by_company
from .forms import RegisterForm, UpdateUserForm, ServiceForm, ResponseForm
from .models import Company, Service, Response, InsuranceType, ValidityType

from redis import StrictRedis

from django.conf import settings
from django.shortcuts import redirect

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from django.views.generic import View
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView

redis = StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


class ServiceListView(ListView):
    """Render 'Service' list of objects, set by 'self.queryset'"""
    paginate_by = 10
    ordering = "title"
    template_name = "index.html"

    def get_queryset(self):
        return search_by_services(self.request)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "found": self.get_queryset().count(),
            "sorting": (
                ("title", "Title: A to Z"),
                ("-title", "Title: Z to A"),
                ("price", "Price: Low to High"),
                ("-price", "Price: High to Low")
            ),
            "companies": Company.objects.values_list("pk", "name"),
            "types": InsuranceType.objects.values_list("pk", "name"),
            "validities": ValidityType.objects.values_list("pk", "name")
        })

        return context


class RegisterView(SuccessMessageMixin, CreateView):
    """View for creating a new 'Company' object, with a response rendered by a template"""
    form_class = RegisterForm
    success_url = "/"
    template_name = "company/register.html"
    success_message = "Registration successful"


class LoginView(SuccessMessageMixin, FormView):
    """A view for user login and rendering a template response"""
    form_class = AuthenticationForm
    success_url = "/"
    template_name = "company/login.html"
    success_message = "You are now logged in"

    def form_valid(self, form):
        user: Company = authenticate(username=form.cleaned_data.get("username"),
                                     password=form.cleaned_data.get("password"))
        if user is not None:
            login(self.request, user)

        return super().form_valid(form)


class LogoutView(LoginRequiredMixin, SuccessMessageMixin, View):
    """A view for user logout from system, implemented only 'GET' function"""
    login_url = "/login"
    success_message = "You have successfully logged out"

    def get(self, request):
        logout(request)
        return redirect("InsuranceApp:index")


class UpdateUserView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """View for updating an 'Company' object, with a response rendered by a template"""
    model = Company
    form_class = UpdateUserForm
    success_url = "/"
    login_url = "/login"
    template_name = "company/update.html"
    success_message = "Profile successful updated"

    def get_object(self, queryset=None):
        return self.request.user


class CompanyServicesView(LoginRequiredMixin, ListView):
    """Render 'Service' list of objects, set by 'get_queryset' function"""
    paginate_by = 10
    ordering = "title"
    login_url = "/login"
    template_name = "services/services.html"

    def get_queryset(self):
        return get_services_by_company(self.request.user.id)


class CreateServiceView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """View for creating a new 'Service' object, with a response rendered by a template"""
    form_class = ServiceForm
    login_url = "/login"
    success_url = "/services"
    template_name = "services/create.html"
    success_message = "Service successful created"

    def form_valid(self, form):
        service: Service = form.save(commit=False)
        service.company = self.request.user
        service.save()

        redis.set(f"services/{service.id}", 0)
        return super().form_valid(form)


class UpdateServiceView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """View for updating an 'Service' object, with a response rendered by a template"""
    model = Service
    form_class = ServiceForm
    login_url = "/login"
    success_url = "/services"
    pk_url_kwarg = "service_id"
    template_name = "services/update.html"
    success_message = "Service successful updated"


class DeleteServiceView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """View for deleting an 'Service' object, with a response rendered by a template"""
    model = Service
    login_url = "/login"
    pk_url_kwarg = "service_id"
    success_url = "/services"
    success_message = "Service successful deleted"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def form_valid(self, form):
        service: Service = form.save()

        redis.delete(f"services/{service.id}")
        return super().form_valid(form)


class ServiceView(SuccessMessageMixin, DetailView, CreateView):
    """Combine class-based view for retrieve 'Service' and return form, with a response rendered by a template"""
    model = Service
    form_class = ResponseForm
    success_url = "/"
    pk_url_kwarg = "service_id"
    template_name = "service.html"
    context_object_name = "service"

    def form_valid(self, form):
        response: Response = form.save(commit=False)
        response.service = Service.objects.get(pk=self.object.id)
        response.company = response.service.company
        response.save()

        send_response_notification.delay({
            "email": response.email,
            "phone": response.phone,
            "full_name": response.full_name,
            "company": response.company.email,
            "service": response.service.title,
            "response_date": response.response_date,
        })

        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        return f"Response to {self.object.company.name} successful created"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        redis.incr(f"services/{self.object.id}")

        if self.object.company.id == self.request.user.id:
            context["views"] = int(redis.get(f"services/{self.object.id}"))

        return context


class ResponsesView(LoginRequiredMixin, ListView):
    """Render 'Response' list of objects, set by 'get_queryset' function"""
    paginate_by = 10
    ordering = "full_name"
    login_url = "/login"
    template_name = "responses.html"

    def get_queryset(self):
        return Response.objects.filter(company=self.request.user)
