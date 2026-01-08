import os
import requests
from django import forms

class AIChatForm(forms.Form):
    
    #метод получение актуального списка моделей
    def get_list_models():
        url = "https://api.intelligence.io.solutions/api/v1/models"

        headers = {"Authorization": os.getenv('AI_KEY')}
        response = requests.get(url, headers=headers)

        models_dict = {k: v for k, v in sorted([(x['id'], x['id'].split('/')[1]) for x in response.json()['data']])}
        return models_dict
    
    MODEL_CHOICES = get_list_models()
    model_ai = forms.ChoiceField(label='Модель ИИ', choices=MODEL_CHOICES)
    message = forms.CharField(label='Ваше сообщение', max_length=500)
    

class WeatherForm(forms.Form):
    location = forms.CharField(label='Название города или населенного пункта',
                               max_length=30,
                               required=False
                               )
    num_days = forms.IntegerField(label='Количество дней',
                                  required=False,
                                  max_value=15)