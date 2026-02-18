from django.urls import path
from site_notes import views

app_name = 'site_notes'

urlpatterns = [
    path('', views.index, name='home'),
    path('notes/', views.ListSections.as_view(), name='notes'),
    path('notes/<slug:section_slug>/', views.ListChapters.as_view(), name='list_chapters'),
    path('notes/<slug:section_slug>/<slug:chapter_text_slug>', views.ChapterText.as_view(), name='chapter_text'),
    path('assistant/', views.assistant, name='assistant'),
    path('weather/', views.weather, name='weather'),
    path('contacts/', views.contacts, name='contacts'),
    path('about/', views.about, name='about')
]