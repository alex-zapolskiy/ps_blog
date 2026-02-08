from django.urls import path
from users import views

urlpatterns = [
        path('registration/', views.registration, name='registration'),
        path('authentication/', views.UserLogin.as_view(), name='login'),
        path('logout/', views.UserLogout.as_view(), name='logout'),
]