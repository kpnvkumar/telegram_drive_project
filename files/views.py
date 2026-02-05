from django.shortcuts import redirect

def dashboard(request):
    if not request.session.get("authenticated"):
        return redirect("login")

    email = request.session.get("user_email")
    return render(request, "dashboard.html", {"email": email})
