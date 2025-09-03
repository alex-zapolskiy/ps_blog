from django.urls import path
from site_notes import views

urlpatterns = [
    path('', views.index),
    path('notes/', views.notes),
    path('assistant/', views.assistant),
    path('contacts/', views.contacts),
    path('about/', views.about)
]