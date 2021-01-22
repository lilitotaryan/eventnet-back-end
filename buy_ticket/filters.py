import django_filters

from authentication.utils import string_to_bool, get_current_time
from .models import Event, Ticket
from user_crud.models import Category
import re
from rest_framework import filters
from django.db.models import Q

class TicketFilter(django_filters.FilterSet):
    is_used = django_filters.CharFilter(field_name="is_used", method='filter_is_used')
    search = django_filters.CharFilter(method='filter_search')


    order_by_field = 'ordering'
    ordering = django_filters.OrderingFilter(
        # fields(('model field name', 'parameter name'),)
        fields= ('event__end_date', )
    )

    class Meta:
        model = Ticket
        fields = ('event__end_date', 'is_used')


    def filter_is_used(self, queryset, name, value):
        # construct the full lrequest.GET.get('states').split(',')
       if value:
            value = string_to_bool(value)
            if value:
                queryset = queryset.filter(Q(is_used = value))
            # else:
            #     queryset = queryset.filter(Q(is_used=value) | Q(event__end_date__gte=get_current_time()))
            return queryset

    def filter_search(self, queryset, name, value):
        # construct the full lrequest.GET.get('states').split(',')
        if value:
            values = value.split('+')
            for i in values:
                i = re.sub(r"[^a-zA-Z0-9]", "", i)
            if value:
                return queryset.filter(Q(event__title__iregex=values) | Q(public_id__iregex=values))