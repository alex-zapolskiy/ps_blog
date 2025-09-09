from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    return render(request, 'site_notes/index.html')

def notes(request):
    return render(request, 'site_notes/notes.html')

def assistant(request):
    return render(request, 'site_notes/assistant.html')

def contacts(request):
    return render(request, 'site_notes/contacts.html')

def about(request):
    return render(request, 'site_notes/about.html')
