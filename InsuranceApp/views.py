from typing import Optional, List
from elasticsearch_dsl.query import MultiMatch

from .documents import ServiceDocument
from .tasks import send_response_notification
from .forms import RegisterForm, UpdateUserForm, ServiceForm, ResponseForm
from .models import Company, Service, Response, InsuranceType, ValidityType

from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout


def index(request: HttpRequest) -> HttpResponse:
    query: str = request.GET.get("query")
    type_id, validity_id, company_id = __get_request_parameters(
        request.GET.get("type"),
        request.GET.get("validity"),
        request.GET.get("company")
    )

    services = ServiceDocument.search()

    if (query is not None) and (query != ""):
        services = services.query(MultiMatch(
            query=query,
            fields=["title", "description", "type.name", "type.risks", "validity.name", "company.name",
                    "company.description", "company.phone"]
        ))

    if type_id is not None:
        services = services.filter("term", **{"type.id": type_id})

    if validity_id is not None:
        services = services.filter("term", **{"validity.id": validity_id})

    if company_id is not None:
        services = services.filter("term", **{"company.id": company_id})

    return render(request, "index.html", {
        "type": type_id,
        "company": company_id,
        "validity": validity_id,
        "services": services.to_queryset(),
        "query": query if query is not None else "",
        "companies": Company.objects.values_list("pk", "name"),
        "types": InsuranceType.objects.values_list("pk", "name"),
        "validities": ValidityType.objects.values_list("pk", "name")
    })


def __get_request_parameters(*args: str) -> List[Optional[int]]:
    return [int(arg) if arg is not None else None for arg in args]


def register_user(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        messages.info(request, "You are now logged in.")
        return redirect("InsuranceApp:index")

    if request.method == "POST":
        register_form = RegisterForm(request.POST)

        if register_form.is_valid():
            user = register_form.save()
            login(request, user)
            messages.success(request, "Registration successful.")

            return redirect("InsuranceApp:index")

        messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        register_form = RegisterForm()

    return render(request, "company/register.html", {"register_form": register_form})


def login_user(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        messages.info(request, "You are now logged in.")
        return redirect("InsuranceApp:index")

    if request.method == "POST":
        login_form = AuthenticationForm(request, data=request.POST)

        if login_form.is_valid():
            user = authenticate(username=login_form.cleaned_data.get("username"),
                                password=login_form.cleaned_data.get("password"))

            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {user.name}.")

                return redirect("InsuranceApp:index")
            messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        login_form = AuthenticationForm()

    return render(request, "company/login.html", {"login_form": login_form})


@login_required(login_url="/login")
def logout_user(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("InsuranceApp:index")


@login_required(login_url="/login")
def update_user(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        update_form = UpdateUserForm(request.POST, instance=request.user)
        update_form.actual_user = request.user

        if update_form.is_valid():
            update_form.save()
            messages.success(request, "Profile successful updated.")

            return render(request, "company/update.html", {"update_form": update_form})
    else:
        update_form = UpdateUserForm(instance=request.user)

    return render(request, "company/update.html", {"update_form": update_form})


@login_required(login_url="/login")
def get_services(request: HttpRequest) -> HttpResponse:
    return render(request, "services/services.html", {
        "services": ServiceDocument.search().filter("term", **{"company.id": request.user.id}).to_queryset()
    })


@login_required(login_url="/login")
def get_responses(request: HttpRequest) -> HttpResponse:
    return render(request, "responses.html", {"responses": Response.objects.filter(company=request.user)})


@login_required(login_url="/login")
def create_service(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        create_form = ServiceForm(request.POST)

        if create_form.is_valid():
            service = create_form.save(commit=False)
            service.company = request.user
            service.save()
            messages.success(request, "Service successful created.")

            return redirect("InsuranceApp:services")
        else:
            messages.error(request, "Unsuccessful service creation. Invalid information.")
    else:
        create_form = ServiceForm()

    return render(request, "services/create.html", {"create_form": create_form})


@login_required(login_url="/login")
def update_service(request: HttpRequest, service_id: int) -> HttpResponse:
    service = Service.objects.get(pk=service_id)

    if request.method == "POST":
        update_form = ServiceForm(request.POST, instance=service)

        if update_form.is_valid():
            update_form.save()
            messages.success(request, "Your service successful updated.")

            return redirect("InsuranceApp:services")
        else:
            messages.error(request, "Unsuccessful service update. Invalid information.")
    else:
        update_form = ServiceForm(instance=service)

    return render(request, "services/update.html", {"update_form": update_form})


@login_required(login_url="/login")
def delete_service(request: HttpRequest, service_id: int) -> HttpResponse:
    Service.objects.get(pk=service_id).delete()
    messages.success(request, "Service successful deleted.")

    return redirect("InsuranceApp:services")


def service_response(request: HttpRequest, service_id: int) -> HttpResponse:
    if request.method == "POST":
        response_form = ResponseForm(request.POST)

        if response_form.is_valid():
            response = response_form.save(commit=False)
            response.service = Service.objects.get(pk=service_id)
            response.company = response.service.company
            response.save()

            send_response_notification.delay({
                "email": response.email,
                "phone": response.phone,
                "full_name": response.full_name,
                "company": response.company.email,
                "service": response.service.title,
                "response_date": response.response_date
            })

            messages.success(request, f"Response to {response.company.name} successful created.")
            return redirect("InsuranceApp:index")
        else:
            messages.error(request, "Unsuccessful response creation. Invalid information.")
    else:
        response_form = ResponseForm()

    return render(request, "service.html", {
        "service": Service.objects.get(pk=service_id),
        "response_form": response_form
    })
