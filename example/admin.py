from django.contrib import admin

from .models import Entry


class EntryAdmin(admin.ModelAdmin):
    list_display = ('title',)
    verbose_name_plural = 'Entries'

admin.site.register(Entry, EntryAdmin)
