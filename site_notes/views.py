from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    return HttpResponse('Главная страница сайта')

def notes(request):
    return HttpResponse('Мои конспекты')

def assistant(request):
    return HttpResponse('Здесь скоро будет ассистент')

def contacts(request):
    return HttpResponse('Здесь будут мои контакты')

def about(request):
    return HttpResponse('О сайте')
