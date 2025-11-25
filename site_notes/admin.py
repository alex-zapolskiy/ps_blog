from django.contrib import admin
from .models import Sections, Chapters
from slugify import slugify

@admin.register(Sections)
class SectionsAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_filter = ('name', )
    search_fields = ('name__icontains',)
    prepopulated_fields = {'slug': ('name',)}
    
    
@admin.register(Chapters)
class ChaptersAdmin(admin.ModelAdmin):
    list_display = ('name', 'section__name')
    list_filter = ('name', )
    list_select_related = ('section', )
    search_fields = ('name__icontains', 'name__istartswith')
    prepopulated_fields = {'slug': ('name',)}
    