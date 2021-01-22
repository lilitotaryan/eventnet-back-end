from django.contrib import admin
from .models import Session


@admin.register(Session)
class Session(admin.ModelAdmin):
    list_display = ['token', 'user', 'is_expired']
