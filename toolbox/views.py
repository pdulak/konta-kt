from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the toolbox index.")


def cleanup_database(request):
    return HttpResponse("Cleanup database")


def initialize_database(request):
    return HttpResponse("Initialize database")
