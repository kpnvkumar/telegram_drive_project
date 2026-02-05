#from django.shortcuts import render
#from accounts.decorators import login_required
import os
import tempfile
import io
from django.http import HttpResponse
from django.shortcuts import render, redirect
from accounts.decorators import login_required
from accounts.db import users_collection
from accounts.telegram_service import upload_file, get_channel_id, list_files, get_file_preview,download_file
from telethon.tl.types import InputPeerChannel
import os
import tempfile
from django.http import FileResponse, Http404
from django.conf import settings


@login_required
def dashboard_view(request):
    email = request.session["user_email"]

    user = users_collection.find_one({"email": email})
    channel_data = user.get("channel_id")

    channel_id = None
    files = []
    if channel_data and isinstance(channel_data, dict):
        channel_id = channel_data['id']
        files = list_files(channel_id)
    elif isinstance(channel_data, int):
        channel_id = channel_data
        files = list_files(channel_id)

    return render(request, "dashboard.html", {
        "channel_id": channel_id,
        "files": files
    })
@login_required
def upload_view(request):
    if request.method == "POST":
        email = request.session["user_email"]
        user = users_collection.find_one({"email": email})

        channel_data = user.get("channel_id")
        if not channel_data or not isinstance(channel_data, dict):
            channel_data = get_channel_id(email)
            users_collection.update_one(
                {"email": email},
                {"$set": {"channel_id": channel_data}},
                upsert=True
            )

        peer = InputPeerChannel(channel_data['id'], channel_data['access_hash'])

        uploaded_file = request.FILES["file"]
        file_name = uploaded_file.name
        uploaded_file.seek(0)

        upload_file(peer, uploaded_file, file_name)

        return redirect("dashboard")
    else:
        return render(request, "upload.html")


@login_required
def file_preview(request, message_id):
    email = request.session["user_email"]
    user = users_collection.find_one({"email": email})
    channel_data = user.get("channel_id")

    if not channel_data:
        return HttpResponse("Channel not found", status=404)

    channel_id = channel_data['id'] if isinstance(channel_data, dict) else channel_data
    preview = get_file_preview(channel_id, int(message_id))

    if preview and preview['type'] == 'image':
        return HttpResponse(preview['data'], content_type=preview['mime_type'])
    else:
        return HttpResponse("Preview not available", status=404)


@login_required
def file_content(request, message_id):
    email = request.session["user_email"]
    user = users_collection.find_one({"email": email})
    channel_data = user.get("channel_id")

    if not channel_data:
        return HttpResponse("Channel not found", status=404)

    channel_id = channel_data['id'] if isinstance(channel_data, dict) else channel_data
    preview = get_file_preview(channel_id, int(message_id))

    if preview and preview['type'] == 'text':
        return render(request, "file_content.html", {
            'file_name': preview['name'],
            'content': preview['content'],
            'message_id': message_id
        })
    else:
        return HttpResponse("File content not available for viewing", status=404)
@login_required
def download(request, message_id):
    email = request.session.get("user_email")
    if not email:
        return redirect("login")

    user = users_collection.find_one({"email": email})
    channel_data = user.get("channel_id")
    print("SESSION:", dict(request.session))
    if not channel_data:
        raise Http404("Channel not found")

    channel_id = channel_data["id"] if isinstance(channel_data, dict) else channel_data

    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, f"file_{message_id}")

    download_file(
        channel_id=channel_id,
        message_id=message_id,
        path=temp_path
    )

    if not os.path.exists(temp_path):
        raise Http404("Download failed")

    return FileResponse(
        open(temp_path, "rb"),
        as_attachment=True,
        filename=f"file_{message_id}"
    )


from accounts.telegram_service import upload_file


