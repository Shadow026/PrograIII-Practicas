from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def hola_mundo (request):
    return HttpResponse("Jaro evri nian")
def saludoNombre (request,nombre,edad):
    return HttpResponse(f"jelou {nombre}, bienvenido, ah pero si tu tienes {edad} años")

def index(request):
    return render(request, 'index.html')