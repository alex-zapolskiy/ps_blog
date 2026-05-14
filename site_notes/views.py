import re
from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.cache import cache
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, DetailView, TemplateView
from .forms import AIChatForm, ContactForm, WeatherForm
from .models import Chapters, ChatMessage, Sections
from .constants.promts import PROMPT_DESCRIPTIONS
from .utils import render_markdown
import markdown2
from .api import APIWeather, APIAIRequest
from django.core.paginator import Paginator
from django.contrib import messages
from .constants.caching_time import SECTIONS_CACHE, CHAPTERS_CACHE, CHAPTERS_TEXT_CACHE, AI_HISTORY_RECORS_CACHE

def index(request):
    return render(request, 'site_notes/index.html', {'title': 'Главная страница'})
            

def weather(request):
    weather_data = None
    error_message = None
    location = None
    num_days = None
    form = None
      
    if request.method == 'GET':
        form = WeatherForm(request.GET)
        if form.is_valid():
            location = form.cleaned_data['location']
            num_days = form.cleaned_data['num_days']
            
            # Устанавливаем значения по умолчанию
            location = location or 'Минск'
            num_days = num_days or 7
            
            # Создаем ключ для кэша
            cache_key = f'weather:{location}:{num_days}'
            
            # Пытаемся получить данные из кэша
            try:
                cached_data = cache.get(cache_key)
            except Exception:
                cached_data = None
            
            if cached_data:
                weather_data = cached_data.get('weather_data')
                error_message = cached_data.get('error_message')
            else:
                result = APIWeather(location, num_days)
                
                if 'error' in result:
                    error_message = result['error']
                    cache_time = 300
                else:
                    weather_data = result.get('weather')
                    cache_time = getattr(settings, 'WEATHER_CACHE_TIMEOUT', 3600)
                
                # Кэшируем результат
                if (weather_data or error_message) and cache_time:
                    try:
                        cache_data = {
                            'weather_data': weather_data,
                            'error_message': error_message,
                        }
                        cache.set(cache_key, cache_data, cache_time)
                    except Exception:
                        pass
    else:
        form = WeatherForm()
    
    if form is None:
        form = WeatherForm()
    
    return render(request, 'site_notes/weather.html', {
        'weather': weather_data,
        'error': error_message,
        'location': location, 
        'num_days': num_days,
        'title': 'Погода',
        'form': form
    })
        
                      
class ListSections(ListView):
    model = Sections
    template_name = 'site_notes/notes.html'
    context_object_name = 'content'

    def get_cache_key(self):
        query = self.request.GET.get('search_sections', '')
        return f'sections_list_{query}'
    
    def get_queryset(self):
        #Ключ для списка разделов
        cache_key = self.get_cache_key()
        queryset = cache.get(cache_key)

        if queryset is None:
            queryset = Sections.objects.all()
            query = self.request.GET.get('search_sections')
            if query:
                safe_query = re.escape(query.strip())
                queryset = queryset.filter(name__iregex=safe_query)

            queryset = list(queryset)
            cache.set(cache_key, queryset, SECTIONS_CACHE)
        
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

    def get_cache_key(self):
        section_slug = self.kwargs.get('section_slug')
        query = self.request.GET.get('search_sections', '')
        return f'chapters_list_{section_slug}_{query}'
    
    def get_queryset(self):
        #Ключ для списка глав
        cache_key = self.get_cache_key()
        queryset = cache.get(cache_key)

        if queryset is None:
            section_slug = self.kwargs.get('section_slug')
            queryset = Chapters.objects.filter(section__slug=section_slug).only('name', 'slug', 'section_id').select_related('section')

            query = self.request.GET.get('search_sections')
            if query:
                safe_query = re.escape(query.strip())
                queryset = Chapters.objects.filter(Q(section__slug=section_slug) & Q(name__iregex=safe_query)).only('name', 'slug', 'section_id').select_related('section')
            
            queryset = list(queryset)
            cache.set(cache_key, queryset, CHAPTERS_CACHE)
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
        #Ключ для объекта главы
        cache_key = f'chapter:{section_slug}:{chapter_slug}'
        chapter = cache.get(cache_key)

        if chapter is None:   
            chapter = get_object_or_404(
                queryset.only('name', 'slug', 'text', 'section_id').select_related('section'),
                section__slug=section_slug,
                slug=chapter_slug
            )
            cache.set(cache_key, chapter, CHAPTERS_TEXT_CACHE)

        return chapter
        
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chapter = self.object
        
        #Ключ для текста главы
        cache_key = f"chapter_md:{chapter.id}"
        
        content_html = cache.get(cache_key)
        
        if content_html is None:
            content_html = markdown2.markdown(
                chapter.text,
                extras=['fenced-code-blocks', 'smarty-pants', 'tables']
            )
            cache.set(cache_key, content_html, CHAPTERS_TEXT_CACHE)
        
        context['title'] = chapter.name
        context['content'] = content_html
        return context  


class AssistantFormView(FormView):
    template_name = 'site_notes/assistant.html'
    form_class = AIChatForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        
        # Обработка GET-параметра history_record
        history_record = self.request.GET.get('history_record')
        if history_record and user.is_authenticated:
            history_item = ChatMessage.objects.filter(public_id=history_record, user=user).first()
            if history_item:
                kwargs['initial'] = {
                    'message': history_item.query,
                    'model_ai': history_item.model_AI,
                    'prompt': history_item.prompt,
                }
                self.loaded_response = history_item.response
            else:
                self.loaded_response = None
        else:
            self.loaded_response = None
            
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # История сообщений
        if user.is_authenticated:
            page_number = self.request.GET.get('history_page', 1)

            cache_key = f'chat_history:{user.id}:{page_number}'
            cached_history = cache.get(cache_key)
            if cached_history is None:
                history_queryset = ChatMessage.objects.filter(user=user)
                paginator = Paginator(history_queryset, 5)
                cached_history = paginator.get_page(page_number)
                cache.set(cache_key, cached_history, AI_HISTORY_RECORS_CACHE)
            
            context['history'] = cached_history
        else:
            context['history'] = None
            
        context['title'] = 'AI Ассистент'
        context['loaded_response'] = getattr(self, 'loaded_response', None)
        return context
    
    def form_valid(self, form):
        user = self.request.user
        message = form.cleaned_data['message']
        model_ai = form.cleaned_data['model_ai']
        prompt = form.cleaned_data['prompt']
        
        # Создание записи в БД для авторизованных пользователей
        chat_obj = None
        if user.is_authenticated:
            chat_obj = ChatMessage.objects.create(
                query=message,
                response='',
                model_AI=model_ai,
                prompt = PROMPT_DESCRIPTIONS[prompt],
                user=user
            )
            #Удаляем кеш истории первой страницы после запроса, т.к. туда попадает новая запись
            cache.delete(f'chat_history:{user.id}:1')

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.stream_response(message, model_ai, prompt, chat_obj)
        
        return super().form_valid(form)
    
    def stream_response(self, message, model_ai, prompt, chat_obj):
        def stream_and_save():
            full_response = ''
            for chunk in APIAIRequest(message, model_ai, prompt):
                full_response += chunk
                yield chunk
            if chat_obj:
                chat_obj.response = render_markdown(full_response)
                chat_obj.save()
        
        return StreamingHttpResponse(
            stream_and_save(),
            content_type='text/markdown'
        )
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Invalid form'}, status=400)
        return super().form_invalid(form)


class ContactView(FormView):
    template_name = 'site_notes/contacts.html'
    form_class = ContactForm
    success_url = reverse_lazy('site_notes:contacts')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Контакты'
        context['socials'] = [
            {
                'name': 'GitHub',
                'url': 'https://github.com/alex-zapolskiy',
                'icon': '🐙'
            },
            {
                'name': 'Telegram',
                'url': 'https://t.me/alex_never',
                'icon': '✈️'
            },
            {
                'name': 'LinkedIn',
                'url': 'https://linkedin.com/in/aliaksandr-zapolskiy',
                'icon': '💼'
            },
        ]
        return context
    
    def form_valid(self, form):
        user = self.request.user
        instance = form.save(commit=False)
        if user.is_authenticated:
            instance.name = instance.name or f'{user.first_name}'
            instance.email = instance.email or user.email
        instance.save()
        messages.success(self.request, 'Сообщение успешно отправлено!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Исправьте ошибки в форме.')
        return super().form_invalid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        if user.is_authenticated:
            initial['name'] = f'{user.first_name}'
            initial['email'] = user.email
        return initial

class AboutView(TemplateView):
    template_name = 'site_notes/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'О сайте'
        return context