import os
import tempfile

from django.http import HttpResponse, FileResponse, Http404, JsonResponse
from django.shortcuts import render, redirect

from accounts.decorators import login_required
from accounts.db import users_collection
from accounts.telegram_service import (upload_file, get_channel_id, list_files,
                                     get_file_preview, download_file)

@login_required
def dashboard_view(request):
    email = request.session.get("user_email")
    user = users_collection.find_one({"email": email})

    if not user or "channel_id" not in user:
        return redirect("login")

    files = list_files(user["channel_id"])
    return render(request, "dashboard.html", {"files": files, "user_email": email})

@login_required
def upload_view(request):
    if request.method == "POST":
        email = request.session.get("user_email")
        user = users_collection.find_one({"email": email})

        if not user or "channel_id" not in user:
            return JsonResponse({"error": "User or channel not found."}, status=400)

        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return JsonResponse({"error": "No file provided."}, status=400)

        file_name = uploaded_file.name

        try:
            upload_file(user["channel_id"], uploaded_file, file_name)
            return redirect("dashboard")
        except Exception as e:
            # It's good practice to log the exception here
            print(f"Error uploading file: {e}")
            return JsonResponse({"error": f"Error uploading file: {e}"}, status=500)

    return redirect("dashboard")


@login_required
def download_view(request, message_id):
    email = request.session.get("user_email")
    if not email:
        return redirect("login")

    user = users_collection.find_one({"email": email})
    channel_data = user.get("channel_id")
    if not channel_data:
        raise Http404("Channel not found")

    channel_id = channel_data["id"] if isinstance(channel_data, dict) else channel_data

    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, f"download_{message_id}")

    file_name = download_file(
        channel_id=channel_id,
        message_id=int(message_id),
        path=temp_path
    )

    if not file_name or not os.path.exists(temp_path):
        raise Http404("Download failed")

    return FileResponse(
        open(temp_path, "rb"),
        as_attachment=True,
        filename=file_name
    )


@login_required
def preview_view(request, message_id):
    email = request.session.get("user_email")
    user = users_collection.find_one({"email": email})

    if not user or "channel_id" not in user:
        return redirect("login")

    preview_data = get_file_preview(user["channel_id"], message_id)

    if not preview_data:
        raise Http404("File not found or preview not available.")

    if preview_data['type'] == 'image':
        response = HttpResponse(preview_data['data'], content_type=preview_data['mime_type'])
        response['Content-Disposition'] = f'inline; filename="{preview_data["name"]}"'
        return response

    if preview_data['type'] == 'text':
        # For security, explicitly set content type for text previews
        # to avoid browser rendering HTML/JS.
        if 'content' in preview_data:
            return HttpResponse(preview_data['content'], content_type='text/plain; charset=utf-8')
        return render(request, "preview_text.html", {"preview": preview_data})

    # For 'file' type and others, show a page with file info and a download link
    return render(request, "preview_file.html", {"preview": preview_data})
