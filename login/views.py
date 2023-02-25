from django.shortcuts import render

def index(request):
    context = {}
    return render(request, 'login/index.html', context)
