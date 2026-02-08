from django.shortcuts import redirect, render
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.urls import reverse_lazy
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


class UserLogin(LoginView):
    template_name = 'authentication.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Вход'
        return context
    

class UserLogout(LogoutView):
    # Указываем, куда перенаправить пользователя после выхода
    next_page = reverse_lazy('login')

