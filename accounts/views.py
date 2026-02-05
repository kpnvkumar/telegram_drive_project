from urllib import request
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from .decorators import login_required
from .db import users_collection
from .utils import hash_password, verify_password
from .otp_service import send_login_otp, validate_otp
from .telegram_service import get_channel_id, get_file_data

def signup_view(request):
    if request.method == "POST":
        email = request.POST["email"].lower()
        password = request.POST["password"]

        # Check if user exists
        if users_collection.find_one({"email": email}):
            return render(request, "signup.html", {"error": "Email already registered"})

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
        email = request.POST["email"].lower()
        password = request.POST["password"]

        user = users_collection.find_one({"email": email})

        if not user or not verify_password(password, user["password"]):
            return render(request, "login.html", {"error": "Invalid email or password"})

        # Send OTP
        send_login_otp(request, email)
        return redirect("otp")

    return render(request, "login.html")


def otp_view(request):
    if request.method == "POST":
        otp = request.POST["otp"]

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
            request.session.set_expiry(3600)  # 1 hour

            return redirect("dashboard")

        return render(request, "otp.html", {"error": "Invalid OTP"})

    return render(request, "otp.html")


@login_required
def download_view(request, message_id):
    email = request.session.get("user_email")
    user = users_collection.find_one({"email": email})

    if not user or "channel_id" not in user:
        return redirect("login")

    file_data = get_file_data(user["channel_id"], message_id)
    if not file_data:
        raise Http404("File not found")

    response = HttpResponse(file_data['data'], content_type=file_data['mime_type'])
    response['Content-Disposition'] = f'attachment; filename="{file_data["name"]}"'
    return response


@login_required
def logout_view(request):
    """Logs the user out by flushing the session."""
    request.session.flush()
    return redirect("login")
