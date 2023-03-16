# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse(
        "Hello, world. You're at the main index.<br><a href='/runs'>Runs</a>"
    )
