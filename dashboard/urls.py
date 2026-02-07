from django.urls import path
from .views import (
    dashboard_view,
    upload_view,
    download_view,
    preview_view,
)

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("upload/", upload_view, name="upload"),
    path("preview/<int:message_id>/", preview_view, name="preview"),
    path("download/<int:message_id>/", download_view, name="download"),
]
