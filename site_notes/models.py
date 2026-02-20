from django.db import models
from django.urls import reverse
from users.models import User

class Sections(models.Model):
    name = models.CharField(max_length=30, )
    slug = models.SlugField(max_length=15, db_index=True, unique=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('list_chapters', kwargs={'section_slug': self.slug})
    
    class Meta:
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'
        ordering = ['name']
    
    
class Chapters(models.Model):
    name = models.CharField(max_length=30, unique=True, null=False)
    slug = models.SlugField(max_length=15, unique=True, db_index=True)
    text = models.TextField(blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    section = models.ForeignKey('Sections', on_delete=models.PROTECT, related_name='chapter', db_index=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('chapter_text', kwargs={'section_slug': self.section.slug, 'chapter_text_slug': self.slug})
    
    class Meta:
        verbose_name = 'Глава'
        verbose_name_plural = 'Главы'
        ordering = ['name']


class AIChatMessage(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='ai_message')
    query = models.TextField(verbose_name='Запрос пользователя')
    responce = models.TextField(blank=True, null=True, verbose_name='Ответ ИИ')
    model_AI = models.CharField(blank=False, default='deepseek-ai/DeepSeek-R1-0528', verbose_name='Модель ИИ')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата запроса')