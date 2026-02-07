from django.shortcuts import redirect, render
from django.http import HttpResponse
from .forms import UserForm


def registration(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserForm()
    return render(request, 'registation.html', {'form': form, 'title': 'Регистация'})


def authentication(request):
    return HttpResponse('<h1>Cтраница аутентификации</h1>')