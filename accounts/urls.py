from django.urls import path
from .views import signup_view, login_view, otp_view, download_view, logout_view

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("otp/", otp_view, name="otp"),
    path("download/<int:message_id>/", download_view, name="download"),
    path("logout/", logout_view, name="logout"),
]
