# from django.urls import path

# from files import views
# from .views import dashboard_view, upload_view, file_preview, file_content

# urlpatterns = [
#     path("", dashboard_view, name="dashboard"),
#     path("upload/", upload_view, name="upload"),
#     path("preview/<int:message_id>/", file_preview, name="file_preview"),
#     path("content/<int:message_id>/", file_content, name="file_content"),
#     path('download/<str:file_id>/', views.download, name='download'),
#     # path('download/<int:file_id>/', views.download_file_view, name='download_file'),
# ]
from django.urls import path
from .views import (
    dashboard_view,
    upload_view,
    file_preview,
    file_content,
    download
)

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("upload/", upload_view, name="upload"),
    path("preview/<int:message_id>/", file_preview, name="file_preview"),
    path("content/<int:message_id>/", file_content, name="file_content"),
    path("download/<int:message_id>/", download, name="download"),
]
