from django.urls import path
from site_notes import views

urlpatterns = [
    path('', views.index, name='home'),
    path('notes/', views.ListSections.as_view(), name='notes'),
    path('notes/<slug:section_slug>/', views.ListChapters.as_view(), name='list_chapters'),
    path('assistant/', views.assistant, name='assistant'),
    path('contacts/', views.contacts, name='contacts'),
    path('about/', views.about, name='about')
]