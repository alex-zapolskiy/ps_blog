import os
import re
import requests
from django import forms
from django.core.cache import cache
from site_notes.constants.promts import PROMPT_DESCRIPTIONS

class AIChatForm(forms.Form):
    
    #метод получение актуального списка моделей
    @staticmethod
    def get_list_models():
        API_KEY = os.getenv('AI_KEY')

        if not API_KEY:
            return {'deepseek-ai/DeepSeek-R1-0528': 'DeepSeek-R1-0528'}
        #пытаемся получить список моделей из кэша
        cached_model = cache.get('ai_model_list')
        if cached_model:
            return cached_model
        
        url = "https://api.intelligence.io.solutions/api/v1/models"
        headers = {"Authorization": API_KEY}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 401:
                return {'deepseek-ai/DeepSeek-R1-0528': 'DeepSeek-R1-0528'}
            response.raise_for_status()

            models_dict = {k: v for k, v in sorted([(x['id'], x['id'].split('/')[1]) for x in response.json()['data']])}
        
        except requests.exceptions.Timeout:
            models_dict = {'deepseek-ai/DeepSeek-R1-0528': 'DeepSeek-R1-0528'}
        except requests.exceptions.ConnectionError:
            models_dict = {'deepseek-ai/DeepSeek-R1-0528': 'DeepSeek-R1-0528'}
        except Exception:
            models_dict = {'deepseek-ai/DeepSeek-R1-0528': 'DeepSeek-R1-0528'}
        #кеширование списка моделей
        cache.set('ai_model_list', models_dict, 3600)
        return models_dict
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['model_ai'].choices = list(self.get_list_models().items())
    
    #MODEL_CHOICES = get_list_models()
    model_ai = forms.ChoiceField(label='Модель ИИ', choices=[])
    prompt = forms.ChoiceField(label='Роль', choices=PROMPT_DESCRIPTIONS)
    message = forms.CharField(
        label='Ваше сообщение',
        max_length=500,
        widget=forms.Textarea(attrs={
            'placeholder': 'Введите ваш вопрос здесь...',
            'rows': 3,
            'style': 'resize: none;'
            })
        )
    

class WeatherForm(forms.Form):
    location = forms.CharField(label='Название города или населенного пункта',
                               max_length=30,
                               required=False
                               )
    num_days = forms.IntegerField(label='Количество дней',
                                  required=False,
                                  min_value=1,
                                  max_value=15)
    
    def clean_location(self):
        location = self.cleaned_data.get('location')
        
        if location:
            if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s-]+$', location):
                raise forms.ValidationError(
                    "Название города может содержать только буквы, пробелы и дефисы."
                )
        
        return location