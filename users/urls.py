from django.urls import path
from users import views

urlpatterns = [
        path('registration/', views.registration, name='registration'),
        path('authentication/', views.UserLogin.as_view(), name='login'),
        path('logout/', views.UserLogout.as_view(), name='logout'),
        path('account/edit/', views.PersonalAccountEditView.as_view(), name='account_edit'),
        path('account/change-password/', views.MyPasswordChangeView.as_view(), name='password_edit'),
        path('account/', views.PersonalAccountView.as_view(), name='account'),

]