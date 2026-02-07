from django.shortcuts import render, redirect
from django.http import HttpResponse
from .decorators import login_required
from .db import users_collection
from .utils import hash_password, verify_password
from .otp_service import send_login_otp, validate_otp
from .telegram_service import get_channel_id


def signup_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").lower()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        # Check if user exists
        if users_collection.find_one({"email": email}):
            return render(request, "signup.html", {"error": "Email already registered"})
        if password != password2:
            return render(request, "signup.html", {"error": "Passwords do not match"})

        users_collection.insert_one({
            "email": email,
            "password": hash_password(password),
            "is_verified": False
        })

        return redirect("login")

    return render(request, "signup.html")


def login_view(request):
    """Login with email & password, send OTP."""
    if request.method == "POST":
        email = request.POST.get("email", "").lower()
        password = request.POST.get("password", "")

        user = users_collection.find_one({"email": email})

        if not user or not verify_password(password, user["password"]):
            return render(request, "login.html", {"error": "Invalid email or password"})

        # Send OTP
        send_login_otp(request, email)
        return redirect("otp")

    return render(request, "login.html")


def otp_view(request):
    if request.method == "POST":
        otp = request.POST.get("otp", "")

        if validate_otp(request, otp):
            email = request.session["otp_email"]

            # get or create channel
            channel_id = get_channel_id(email)

            # save channel id
            users_collection.update_one(
                {"email": email},
                {"$set": {"channel_id": channel_id}},
                upsert=True
            )

            request.session["authenticated"] = True
            request.session["user_email"] = email
            del request.session["otp_secret"]
            del request.session["otp_email"]
            request.session.set_expiry(3600)  # 1 hour

            return redirect("dashboard")

        return render(request, "otp.html", {"error": "Invalid OTP"})

    return render(request, "otp.html")


def resend_otp_view(request):
    """Resends the OTP code to the user's email."""
    email = request.session.get("otp_email")
    if not email:
        # If for some reason the email is not in the session,
        # redirect to the login page.
        return redirect("login")

    send_login_otp(request, email)
    return redirect("otp")


@login_required
def logout_view(request):
    """Logs the user out by flushing the session."""
    request.session.flush()
    return redirect("login")
