from django.shortcuts import redirect

def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_email"):
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper


