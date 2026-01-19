from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def login_view(request):
    return render(request, "login.html")

def registro_view(request):
    return render(request, "registro.html")

@login_required
def propietario_view(request):
    return render(request, "propietario_feed.html")

@login_required
def jornalero_view(request):
    return render(request, "jornalero_feed.html")
