from django.shortcuts import render
from django.http import HttpResponse


def registration(request):
    return HttpResponse('<h1>Cтраница регистрации</h1>')


def authentication(request):
    return HttpResponse('<h1>Cтраница аутентификации</h1>')