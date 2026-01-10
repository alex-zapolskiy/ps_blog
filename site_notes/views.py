import os
import re
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render
from django.db.models import Q
from django.views.generic import ListView, DetailView
from site_notes.forms import AIChatForm, WeatherForm
from site_notes.models import Chapters, Sections
import json
import requests
import markdown2


def index(request):
    return render(request, 'site_notes/index.html', {'title': 'Главная страница'})
            

def weather(request):
    weather_data = None
    error_message = None
    location = None
    num_days = None
      
    if request.method == 'GET':
        form = WeatherForm(request.GET)
        if form.is_valid():
            location = form.cleaned_data['location']
            num_days = form.cleaned_data['num_days']
            
            #Устанавливаем значения по умолчанию, если поля пустые
            if not location:
                location = 'Минск'
                
            if not num_days:
                num_days = 7
                
            # Получаем данные о погоде
            result = APIWeather(location, num_days)
            
            #Проверка на присутвствие ошибок
            if 'error' in result:
                error_message = result['error']
            else:
                weather_data = result['weather']
            
            return render(request, 'site_notes/weather.html', {
                'weather': weather_data,
                'error': error_message,
                'location': location, 
                'num_days': num_days,
                'form': form,
                'title': 'Погода'
            })
        else:
            form = WeatherForm(request.GET)
    else:
        form = WeatherForm()
    
    # return render(request, 'site_notes/weather.html', {
    #     'weather': weather, 
    #     'location': location, 
    #     'num_days': num_days,
    #     'form': form
    # })
    
    
def APIWeather(location, num_days):
    API_KEY = os.getenv('WEATHER_API_KEY')
    BASE_URL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'
    
    url = f'{BASE_URL}{location}'
    
    params = {
    'key': API_KEY,
    'unitGroup': 'metric',
    'lang': 'ru',
    'contentType': 'json'
    }
    
    try:
        responce = requests.get(url=url, params=params)
        responce.raise_for_status()
        
        data = responce.json()
        if 'days' not in data or not data['days']:
            return {'error': 'Данные о погоде для указанного города не найдены'}
        
        result = [(day['datetime'], day['description'], day['tempmax'], day['tempmin']) for day in responce.json()['days'][:num_days]]
        return {'weather': result}
    
    except requests.exceptions.HTTPError as http_err:
        if responce.status_code == 400:
            return {'error': 'Неверное название города. Пожалуйста, проверьте правильность ввода'}
        elif responce.status_code == 401:
            return {'error': 'Ошибка аутентификации API ключа'}
        elif responce.status_code == 404:
            return {'error': 'Город не найден. Пожалуйста, проверьте правильность названия'}
        else:
            return {'error': f'Ошибка при запросе погоды: {responce.status_code}'}
        
        
class ListSections(ListView):
    model = Sections
    template_name = 'site_notes/notes.html'
    context_object_name = 'content'
    
    def get_queryset(self):
        queryset = Sections.objects.all()
        query = self.request.GET.get('search_sections')
        if query:
            safe_query = re.escape(query.strip())
            queryset = Sections.objects.filter(name__iregex=safe_query)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Конспекты'
        context['form_text'] = 'Введите запрос на поиск по разделам'
        context['search_query'] = self.request.GET.get('search_sections', '')
        context['reset_url'] = self.get_reset_url()
        return context

    def get_reset_url(self):
        return self.request.path

class ListChapters(ListSections):
    model = Chapters

    def get_queryset(self):
        section_slug = self.kwargs.get('section_slug')
        queryset = Chapters.objects.filter(section__slug=section_slug).only('name', 'slug', 'section_id').select_related('section')
        query = self.request.GET.get('search_sections')
        if query:
            safe_query = re.escape(query.strip())
            queryset = query = Chapters.objects.filter(Q(section__slug=section_slug) & Q(name__iregex=safe_query)).only('name', 'slug', 'section_id').select_related('section')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_text'] = 'Введите запрос на поиск по главам'
        context['search_query'] = self.request.GET.get('search_sections', '')
        return context

class ChapterText(DetailView):
    model = Chapters
    template_name = 'site_notes/chapter_text.html'
    slug_url_kwarg = 'chapter_text_slug'
    context_object_name = 'chapter'
    
    def get_object(self, queryset = None):
        if queryset is None:
            queryset = self.get_queryset()
        section_slug = self.kwargs.get('section_slug')
        chapter_slug = self.kwargs.get('chapter_text_slug')
        
        return queryset.filter(section__slug=section_slug,
            slug=chapter_slug).only('name', 'slug', 'text', 'section_id'
                                    ).select_related('section').get()
        
        
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chapter = self.object
        context['title'] = chapter.name
        context['content'] = markdown2.markdown(chapter.text)
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
            
            return render(request, 'site_notes/assistant.html', {'form': form, 'title': 'AI Ассистент'})
    else:
        form = AIChatForm()
    return render(request, 'site_notes/assistant.html', {'form': form, 'title': 'AI Ассистент'})

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