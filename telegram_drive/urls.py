from django.shortcuts import redirect
from django.urls import path, include

urlpatterns = [
    # All URLs are now at the root level for consistency.
    path("", include("accounts.urls")),
    path("", include("dashboard.urls")),
]
