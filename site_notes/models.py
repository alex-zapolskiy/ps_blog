from django.db import models
from django.urls import reverse

class Sections(models.Model):
    name = models.CharField(max_length=30, )
    slug = models.SlugField(max_length=15, db_index=True, unique=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('list_chapters', kwargs={'section_slug': self.slug})
    
    
class Chapters(models.Model):
    name = models.CharField(max_length=30, unique=True, null=False)
    slug = models.SlugField(max_length=15, unique=True, db_index=True)
    text = models.TextField(blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    section = models.ForeignKey('Sections', on_delete=models.PROTECT, related_name='chapter')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('chapter_text', kwargs={'section_slug': self.section.slug, 'chapter_text_slug': self.slug})