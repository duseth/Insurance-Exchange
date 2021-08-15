from .tasks import send_response_notification
from .forms import RegisterForm, UpdateUserForm, ServiceForm, ResponseForm
from .models import Company, Service, Response, InsuranceType, ValidityType
from .services import search_by_services, get_services_by_company, convert_response_to_notification

from redis import StrictRedis
from typing import Optional, List

from django.conf import settings
from django.contrib import messages
from django.db.models import QuerySet
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout

redis = StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


def index(request: HttpRequest) -> HttpResponse:
    """Index view handler responsible to get 'service' objects by query and filters"""
    services: QuerySet = search_by_services(request)

    paginator = Paginator(services, 10)
    page_number = request.GET.get("page")

    sorting: Dict[str, str] = {
        "title": "Title: A to Z",
        "-title": "Title: Z to A",
        "price": "Price: Low to High",
        "-price": "Price: High to Low"
    }

    return render(request, "index.html", {
        "found": len(services),
        "sorting": sorting.items(),
        "services": paginator.get_page(page_number),
        "companies": Company.objects.values_list("pk", "name"),
        "types": InsuranceType.objects.values_list("pk", "name"),
        "validities": ValidityType.objects.values_list("pk", "name")
    })


def register_user(request: HttpRequest) -> HttpResponse:
    """Register user view handler responsible for registration user in system"""
    if request.user.is_authenticated:
        messages.info(request, "You are now logged in.")
        return redirect("InsuranceApp:index")

    if request.method == "POST":
        register_form: RegisterForm = RegisterForm(request.POST)

        if register_form.is_valid():
            user: Company = register_form.save()
            login(request, user)
            messages.success(request, "Registration successful.")

            return redirect("InsuranceApp:index")

        messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        register_form: RegisterForm = RegisterForm()

    return render(request, "company/register.html", {"register_form": register_form})


def login_user(request: HttpRequest) -> HttpResponse:
    """Login user view handler responsible for login in system"""
    if request.user.is_authenticated:
        messages.info(request, "You are now logged in.")
        return redirect("InsuranceApp:index")

    if request.method == "POST":
        login_form: AuthenticationForm = AuthenticationForm(request, data=request.POST)

        if login_form.is_valid():
            user: Company = authenticate(username=login_form.cleaned_data.get("username"),
                                         password=login_form.cleaned_data.get("password"))

            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {user.name}.")

                return redirect("InsuranceApp:index")
            messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        login_form: AuthenticationForm = AuthenticationForm()

    return render(request, "company/login.html", {"login_form": login_form})


@login_required(login_url="/login")
def logout_user(request: HttpRequest) -> HttpResponse:
    """Login logout view handler responsible for logout from system"""
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("InsuranceApp:index")


@login_required(login_url="/login")
def update_user(request: HttpRequest) -> HttpResponse:
    """Update user view handler responsible for update user object"""
    if request.method == "POST":
        update_form: UpdateUserForm = UpdateUserForm(request.POST, instance=request.user)
        update_form.actual_user = request.user

        if update_form.is_valid():
            update_form.save()
            messages.success(request, "Profile successful updated.")

            return render(request, "company/update.html", {"update_form": update_form})
    else:
        update_form: UpdateUserForm = UpdateUserForm(instance=request.user)

    return render(request, "company/update.html", {"update_form": update_form})


@login_required(login_url="/login")
def get_services(request: HttpRequest) -> HttpResponse:
    """Services view handler responsible for 'service' objects dispatching from 'company'"""
    return render(request, "services/services.html", {"services": get_services_by_company(request.user.id)})


@login_required(login_url="/login")
def get_responses(request: HttpRequest) -> HttpResponse:
    """Responses view handler responsible for 'response' objects dispatching from 'company'"""
    return render(request, "responses.html", {"responses": Response.objects.filter(company=request.user)})


@login_required(login_url="/login")
def create_service(request: HttpRequest) -> HttpResponse:
    """Create service view handler responsible for creating 'service' object"""
    if request.method == "POST":
        create_form: ServiceForm = ServiceForm(request.POST)

        if create_form.is_valid():
            service: Service = create_form.save(commit=False)
            service.company = request.user
            service.save()

            redis.set(f"services/{service.id}", 0)
            messages.success(request, "Service successful created.")

            return redirect("InsuranceApp:services")
        else:
            messages.error(request, "Unsuccessful service creation. Invalid information.")
    else:
        create_form: ServiceForm = ServiceForm()

    return render(request, "services/create.html", {"create_form": create_form})


@login_required(login_url="/login")
def update_service(request: HttpRequest, service_id: int) -> HttpResponse:
    """Update service view handler responsible for updating 'service' object"""
    service: QuerySet = Service.objects.get(pk=service_id)

    if request.method == "POST":
        update_form: ServiceForm = ServiceForm(request.POST, instance=service)

        if update_form.is_valid():
            update_form.save()
            messages.success(request, "Your service successful updated.")

            return redirect("InsuranceApp:services")
        else:
            messages.error(request, "Unsuccessful service update. Invalid information.")
    else:
        update_form: ServiceForm = ServiceForm(instance=service)

    return render(request, "services/update.html", {"update_form": update_form})


@login_required(login_url="/login")
def delete_service(request: HttpRequest, service_id: int) -> HttpResponse:
    """Delete service view handler responsible for deleting 'service' object"""
    Service.objects.get(pk=service_id).delete()

    redis.delete(f"services/{service_id}")
    messages.success(request, "Service successful deleted.")

    return redirect("InsuranceApp:services")


def service_response(request: HttpRequest, service_id: int) -> HttpResponse:
    """Service response view handler responsible for:
        GET: return 'service' details
        POST: create 'response' object and Celery notification task"""
    if request.method == "POST":
        response_form: ResponseForm = ResponseForm(request.POST)

        if response_form.is_valid():
            response: Response = response_form.save(commit=False)
            response.service = Service.objects.get(pk=service_id)
            response.company = response.service.company
            response.save()

            send_response_notification.delay(convert_response_to_notification(response))

            messages.success(request, f"Response to {response.company.name} successful created.")
            return redirect("InsuranceApp:index")
        else:
            messages.error(request, "Unsuccessful response creation. Invalid information.")
    else:
        redis.incr(f"services/{service_id}")
        response_form: ResponseForm = ResponseForm()

    service = Service.objects.get(pk=service_id)

    return render(request, "service.html", {
        "service": service,
        "response_form": response_form,
        "views": int(redis.get(f"services/{service_id}")) if service.company.id == request.user.id else None
    })
