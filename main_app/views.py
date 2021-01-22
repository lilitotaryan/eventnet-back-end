from django.http import HttpResponse

def index(request):
    return HttpResponse("<html><body>EventNet API.</body></html>")