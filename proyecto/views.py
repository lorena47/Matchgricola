from django.shortcuts import render

def login_view(request):
    return render(request, "login.html")

def registro_view(request):
    return render(request, "registro.html")

def propietario_view(request):
    return render(request, "propietario_feed.html")

def jornalero_view(request):
    return render(request, "jornalero_feed.html")
