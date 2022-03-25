from django.http import HttpResponse

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse("<a href='/logout/''>You are not authorized on this page!</a>")
        return wrapper_func
    return decorator

def admin_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        return HttpResponse("<a href='/logout/'>You are in the viewer's page.</a>")
    return wrapper_func