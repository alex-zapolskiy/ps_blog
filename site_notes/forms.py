from django import forms

class AIChatForm(forms.Form):
    MODEL_CHOICES = [
                        ('deepseek-ai/DeepSeek-R1-0528', 'DeepSeek R1'),
                        ('swiss-ai/Apertus-70B-Instruct-2509', 'Apertus 70B'),
                        ('meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8', 'Llama 4 Maverick'),
                        ('openai/gpt-oss-120b', 'GPT OSS 120B'),
                        ('Intel/Qwen3-Coder-480B-A35B-Instruct-int4-mixed-ar', 'Qwen3 Coder 480B'),
                        ('Qwen/Qwen3-Next-80B-A3B-Instruct', 'Qwen3 Next 80B'),
                        ('openai/gpt-oss-20b', 'GPT OSS 20B'),
                        ('Qwen/Qwen3-235B-A22B-Thinking-2507', 'Qwen3 235B Thinking'),
                        ('mistralai/Magistral-Small-2506', 'Magistral Small'),
                        ('mistralai/Devstral-Small-2505', 'Devstral Small'),
                        ('LLM360/K2-Think', 'K2 Think'),
                        ('meta-llama/Llama-3.3-70B-Instruct', 'Llama 3.3 70B'),
                        ('mistralai/Mistral-Large-Instruct-2411', 'Mistral Large'),
                        ('Qwen/Qwen2.5-VL-32B-Instruct', 'Qwen2.5 VL 32B'),
                        ('meta-llama/Llama-3.2-90B-Vision-Instruct', 'Llama 3.2 90B Vision'),
                    ]
    
    model_ai = forms.ChoiceField(label='Модель ИИ', choices=MODEL_CHOICES)
    message = forms.CharField(label='Ваше сообщение', max_length=500)
