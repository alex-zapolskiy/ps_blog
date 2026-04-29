import json
import os
import requests
from .constants.promts import SYSTEM_PROMPTS

def APIWeather(location, num_days):
    
    API_KEY = os.getenv('WEATHER_API_KEY')
    if not API_KEY:
        return {'error': 'Сервис погоды временно недоступен (ошибка конфигурации)'}
    
    BASE_URL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'
    url = f'{BASE_URL}{location}'
    
    params = {
        'key': API_KEY,
        'unitGroup': 'metric',
        'lang': 'ru',
        'contentType': 'json'
    }
    
    try:
        response = requests.get(url=url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'days' not in data or not data['days']:
            return {'error': 'Данные о погоде для указанного города не найдены'}
        
        result = [
            (day['datetime'], day['description'], day['tempmax'], day['tempmin']) 
            for day in data['days'][:num_days]
        ]
        
        return {'weather': result}
    
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response.status_code else 0
        
        if status_code == 400:
            return {'error': 'Неверное название города. Проверьте правильность ввода'}
        
        elif status_code == 401:
            return {'error': 'Ошибка аутентификации API ключа'}
        
        elif status_code == 404:
            return {'error': f'Город "{location}" не найден. Проверьте название'}
        else:
            return {'error': f'Ошибка при запросе погоды (код: {status_code})'}
    
    except json.JSONDecodeError:
        return {'error': 'Сервер погоды вернул некорректные данные'}
    
    except Exception:
        return {'error': 'Сервис погоды временно недоступен'}
        

def APIAIRequest(user_input=None, model_ai=None, prompt=None):
    #запрос к ИИ
    API_KEY = os.getenv('AI_KEY')

    if not API_KEY:
        yield 'Ошибка: API ключ не настроен'
        return
    
    url = 'https://api.intelligence.io.solutions/api/v1/chat/completions'

    headers = {'Authorization': API_KEY}
    model_ai =  model_ai if model_ai else 'deepseek-ai/DeepSeek-R1-0528'
    prompt = prompt if prompt else SYSTEM_PROMPTS['writer']
    user_content = user_input
    
    data = {
        'model': model_ai,
        'messages': [
            SYSTEM_PROMPTS[prompt],
            {
                'role': 'user',
                'content': user_content
            }
        ],
        'stream': True
    }

    try:        
        response = requests.post(
            url,
            headers=headers,
            json=data,
            stream=True,
            timeout=30)
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
        elif response.status_code == 401:
            yield 'Ошибка: неверный API ключ'
        elif response.status_code == 429:
            yield 'Ошибка: превышен лимит запросов, пропробуйте позже'
        elif response.status_code == 503:
            yield 'Ошибка: сервис временно недоступен'
        else:
            yield f'Ошибка: HTTP {response.status_code}'
        
    except requests.exceptions.Timeout:
        yield 'Ошибка: сервер не ответил вовремя. Попробуйте позже'
    except requests.exceptions.ConnectionError:
        yield 'Ошибка: нет подключения к сервису'
    except requests.exceptions.RequestException as e:
        yield f'Ошибка при запросе: {str(e)}'
    