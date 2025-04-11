from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Hola desde la vista index de la app web.")