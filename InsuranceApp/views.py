from .forms import RegisterForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


def user_register(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")

            return redirect("InsuranceApp:index")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = RegisterForm()

    return render(request, "register.html", {"register_form": form})


def user_login(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {user.name}.")

                return redirect("InsuranceApp:index")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")

    form = AuthenticationForm()
    return render(request, "login.html", {"login_form": form})


def user_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("InsuranceApp:index")
