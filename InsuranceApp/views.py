from .tasks import *
from .forms import *
from .models import *
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html", {"services": Service.objects.all()})


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
        update_form = UpdateProfileForm(request.POST, instance=request.user)
        update_form.actual_user = request.user

        if update_form.is_valid():
            update_form.save()
            messages.success(request, "Profile successful updated.")

            return render(request, "company/update.html", {"update_form": update_form})
    else:
        update_form = UpdateProfileForm(instance=request.user)

    return render(request, "company/update.html", {"update_form": update_form})


@login_required(login_url="/login")
def get_services(request: HttpRequest) -> HttpResponse:
    return render(request, "services/services.html", {"services": Service.objects.filter(company=request.user)})


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
                "company": response.company.email,
                "service": response.service.title,
                "full_name": response.full_name,
                "email": response.email,
                "phone": response.phone,
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
