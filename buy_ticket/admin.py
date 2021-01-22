from django.contrib import admin

# Register your models here.
from buy_ticket.models import Ticket, Payment


@admin.register(Ticket)
class Ticket(admin.ModelAdmin):
    list_display = ['public_id', 'event', 'user', 'is_used']


@admin.register(Payment)
class Payment(admin.ModelAdmin):
    list_display = ['public_id', 'user', 'is_expired', 'reason']
