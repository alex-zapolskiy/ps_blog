from django.contrib import admin
from .models import Sections, Chapters, ContactMessage
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
    

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'time_create', 'is_read']
    list_filter = ['is_read']
    list_editable = ['is_read']
    readonly_fields = ['name', 'email', 'message', 'time_create']