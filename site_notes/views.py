from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from site_notes.models import Chapters, Sections


def index(request):
    return render(request, 'site_notes/index.html')

class ListSections(ListView):
    model = Sections
    template_name = 'site_notes/notes.html'
    context_object_name = 'content'
    
    def get_queryset(self):
        return Sections.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Конспекты'
        return context


class ListChapters(ListSections):
    model = Chapters

    def get_queryset(self):
        section_slug = self.kwargs.get('section_slug')
        return Chapters.objects.filter(section__slug=section_slug)
    

class ChapterText(DetailView):
    model = Chapters
    template_name = 'site_notes/chapter_text.html'
    slug_url_kwarg = 'chapter_text_slug'
    context_object_name = 'chapter'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['chapter'].name
        return context
        


def assistant(request):
    return render(request, 'site_notes/assistant.html')

def contacts(request):
    return render(request, 'site_notes/contacts.html')

def about(request):
    return render(request, 'site_notes/about.html')
