from django.shortcuts import redirect, render
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, DetailView, TemplateView
from django.http import HttpResponse
from django.urls import reverse_lazy
from .models import User
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


class PersonalAccountView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'personal_account.html'
    display_fields = ['username', 'email', 'first_name', 'last_name', 'birth_data']

    def get_object(self):
        return User.objects.only(*self.display_fields).get(pk=self.request.user.pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object
        context['title'] = 'Личный кабинет'
        context['user_fields'] = [
            {
                'label': obj._meta.get_field(name).verbose_name.capitalize(),
                'value': getattr(obj, name)
             }
             for name in self.display_fields
            ]
        return context
    

class PersonalAccountEditView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'personal_account_edit.html'
    fields = ['username', 'email', 'first_name', 'last_name', 'birth_data']

    def get_object(self):
        return self.request.user
    
    def get_success_url(self):
        return reverse_lazy('account')
    

class MyPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'password_edit.html'
    form_class = PasswordChangeForm

    def get_success_url(self):
        return reverse_lazy('home')