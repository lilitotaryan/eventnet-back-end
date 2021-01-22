import django_filters

from authentication.utils import string_to_bool
from .models import Event
from user_crud.models import Category
import re
from rest_framework import filters
from django.db.models import Q

class EventFilter(django_filters.FilterSet):
    # title = django_filters.CharFilter(field_name="title", lookup_expr='icontains')
    # description = django_filters.CharFilter(field_name="description", lookup_expr='icontains')
    is_responsible = django_filters.CharFilter(field_name="is_responsible", method='filter_bool')
    categories = django_filters.CharFilter(method='filter_categories')
    address__state = django_filters.CharFilter(method='filter_address__state')
    address__city = django_filters.CharFilter(method='filter_address__city')
    search = django_filters.CharFilter(method='filter_search')


    order_by_field = 'ordering'
    ordering = django_filters.OrderingFilter(
        # fields(('model field name', 'parameter name'),)
        fields= ('ticket_fee', 'start_date', )
    )

    # search_by_field = 'searching'
    # search_fields = filters.SearchFilter(
    #     # fields(('model field name', 'parameter name'),)
    #     fields= ('title', 'description', )
    # )

    class Meta:
        model = Event
        fields = ('is_responsible', 'categories', 'address__state', 'address__city', 'ticket_fee', 'start_date')


    def filter_address__state(self, queryset, name, value):
        # construct the full lrequest.GET.get('states').split(',')
       if value:
            values = value.split(',')
            values = [re.sub(r"[^a-zA-Z]", "", i) for i in values]
            return queryset.filter(address__state__in=values)

    def filter_address__city(self, queryset, name, value):
        # construct the full lrequest.GET.get('states').split(',')
       if value:
            values = value.split(',')
            values = [re.sub(r"[^a-zA-Z]", "", i) for i in values]
            return queryset.filter(address__city__in=values)

    def filter_categories(self, queryset, name, value):
        # construct the full lrequest.GET.get('states').split(',')
       if value:
            values = value.split(',')
            values = [re.sub(r"[^a-zA-Z]", "", i) for i in values]
            return queryset.filter(categories__name__in=values)

    def filter_bool(self, queryset, name, value):
        # construct the full lrequest.GET.get('states').split(',')
       if value:
            value = string_to_bool(value)
            return queryset.filter(**{name: value})

    def filter_search(self, queryset, name, value):
        if value:
            values = value.split('+')
            for i in values:
                i = re.sub(r"[^a-zA-Z0-9]", "", i)
            if value:
                return queryset.filter(Q(title__iregex=values) | Q(description__iregex=values))
