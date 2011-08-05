# Create your views here.
from bodhi.models import *  
from django.http import HttpResponse

def index(request):
    return HttpResponse("Zen&TIC")
