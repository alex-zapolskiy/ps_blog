import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse

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


class ChatMessage(models.Model):
        public_id = models.UUIDField(default=uuid.uuid4, editable=True, db_index=True, unique=True)
        query = models.TextField(verbose_name='Запрос пользователя')
        response = models.TextField(blank=True, null=True, verbose_name='Ответ ИИ')
        model_AI = models.CharField(default='deepseek-ai/DeepSeek-R1-0528', verbose_name='Модель ИИ')
        time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата запроса')
        user = models.ForeignKey(to= settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_messages')

        class Meta:
            verbose_name = 'Сообщения чата'
            verbose_name_plural = 'Сообщении чата'
            ordering = ['-time_create']

        @property
        def model_after_slash(self):
            if '/' in self.model_AI:
                return self.model_AI.split('/')[1]
            return self.model_AI