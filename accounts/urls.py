from django.urls import path
from .views import (
    signup_view,
    login_view,
    otp_view,
    resend_otp_view,
    logout_view,
)

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("otp/", otp_view, name="otp"),
    path("resend_otp/", resend_otp_view, name="resend_otp"),
    path("logout/", logout_view, name="logout"),
]
