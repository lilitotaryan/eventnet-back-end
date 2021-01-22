from django.contrib import admin

# Register your models here.
from subscribe.models import Subscriber


@admin.register(Subscriber)
class Subscriber(admin.ModelAdmin):
    list_display = ['email', 'amount_of_subscription_emails', 'last_subscription_email_date']

