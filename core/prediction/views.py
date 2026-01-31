from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime

from .models import Profile
from .utils import predict_rf, predict_dt, predict_prophet

def home(request):
    if request.user.is_authenticated:
        # Logged-in users go directly to prediction
        return redirect("predict")

    # New users must login or register
    return render(request, "auth/home.html")


# -------------------------
# REGISTER
# -------------------------
def user_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        User.objects.create_user(username=username, password=password)
        user = User.objects.get(username=username)
        Profile.objects.create(user=user, role="USER")

        return redirect("login")

    return render(request, "auth/register.html")


# -------------------------
# LOGIN
# -------------------------
def user_login(request):
    if request.method == "POST":
        user = authenticate(
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user:
            login(request, user)
            next_url = request.GET.get("next")
            return redirect(next_url or "predict")

    return render(request, "auth/login.html")


# -------------------------
# LOGOUT
# -------------------------
def user_logout(request):
    logout(request)
    return redirect("login")


# -------------------------
# PREDICTION (PROTECTED)
# -------------------------
@login_required(login_url="login")
def predict_view(request):
    if request.method == "POST":
        date_str = request.POST.get("date")
        hour = int(request.POST.get("hour"))
        station = request.POST.get("station")

        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        dayofweek = date_obj.weekday()

        rf_pred = predict_rf(
            station,
            date_obj.year,
            date_obj.month,
            date_obj.day,
            hour,
            dayofweek,
        )

        dt_pred = predict_dt(
            station,
            date_obj.year,
            date_obj.month,
            date_obj.day,
            hour,
            dayofweek,
        )

        prophet_pred = predict_prophet(date_obj)

        return render(
            request,
            "prediction/result.html",
            {
                "rf_pred": rf_pred,
                "dt_pred": dt_pred,
                "prophet_pred": prophet_pred,
                "station": station,
                "date": date_str,
                "hour": hour,
            },
        )

    return render(request, "prediction/index.html")
