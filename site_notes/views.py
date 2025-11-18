import os
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from site_notes.forms import AIChatForm
from site_notes.models import Chapters, Sections
import json
import requests
import time


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
    
    if request.method == 'POST':
        form = AIChatForm(request.POST)
        if form.is_valid():
            #получаем "чистые" данные из формы
            message = form.cleaned_data['message']
            model_ai = form.cleaned_data['model_ai']
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return StreamingHttpResponse(
                    AIRequest(message, model_ai), 
                    content_type='text/plain'
                )
            
            return render(request, 'site_notes/assistant.html', {'form': form})
    else:
        form = AIChatForm()
    return render(request, 'site_notes/assistant.html', {'form': form})

def contacts(request):
    return render(request, 'site_notes/contacts.html')

def about(request):
    return render(request, 'site_notes/about.html')

def AIRequest(user_input=None, model_ai=None):
    #запрос к ИИ
    url = 'https://api.intelligence.io.solutions/api/v1/chat/completions'

    headers = {'Authorization': os.getenv('AI_KEY')}
    model_ai =  model_ai if model_ai else 'deepseek-ai/DeepSeek-R1-0528'
    user_content = user_input
    
    data = {
        'model': model_ai,
        'messages': [
            {
                'role': 'system',
                'content': 'You\'re a helpful assistant. Answer briefly and to the point, without wasting time thinking out loud.'
            },
            {
                'role': 'user',
                'content': user_content
            }
        ],
        'stream': True
    }
    
    response = requests.post(url, headers=headers, json=data, stream=True)
    #обработка ответа и парсинг json
    if response.status_code == 200:
        for line in response.iter_lines(decode_unicode=True):
            if line:
                if line.startswith('data: '):
                    chunk_data = line[6:]

                    if chunk_data == '[DONE]':
                        break
                    
                    try:
                        chunk_json = json.loads(chunk_data)
                        if 'choices' in chunk_json and len(chunk_json['choices']) > 0:
                            choice = chunk_json['choices'][0]
                            if 'delta' in choice and 'content' in choice['delta']:
                                content = choice['delta']['content']
                                yield content
                    
                    except json.JSONDecodeError:
                        continue
                    except (KeyError, IndexError):
                        continue
    else:
        yield f'Ошибка: HTTP {response.status_code}'