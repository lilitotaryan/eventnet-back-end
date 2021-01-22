import stripe
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

from authentication.permissions import ApiTokenPermission, LoggedInPermission, UserVerified
from authentication.serializers import error_many_list_serializer
from authentication.utils import response, string_to_bool, string_to_int, get_current_date, get_current_time
from buy_ticket.filters import TicketFilter
from event_crud.errors import UserHasNoEvent, EventHasNoAddress, CannotDeleteEventHavingTickets, \
    UserCanBuyAtMostFreeTickets
from event_crud.permissions import CompanyUserPermission, CompanyEventPossessionPermission, \
    CompanyCoCompanyEventPossessionPermission
from event_crud.serializers import EventCreateSerializer, EventUpdateSerializer, EventCompanyUser, \
    EventFilterSerializer, FreeTicketCreateSerializer
from buy_ticket.errors import StripeError
from main_app.api_exceptions import NotFound, EventNotFound, UserPermission, NoPaymentIsMade
from django.conf import settings

from main_app.constants import TICKET_AMOUNT
from subscribe.task import send_celery_email
from .utils import refund_all_event_users
from user_crud.errors import UserHasAddress, AddressDataNotValid
from user_crud.serializers import CategoryUserSerializer, AddressSerializer
from .filters import EventFilter
from .models import Event
from buy_ticket.models import Ticket, Payment
from authentication.errors import ValidationError, UnexpectedError
from user_crud.models import Address
from authentication.models import CustomUser
from event_crud.models import Event
from django.db.models import Q, Subquery
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# from django_filters import rest_framework as filters
from rest_framework import filters

stripe.api_key = settings.STRIPE_API_KEY

class AllEvents(APIView):
    permission_classes = [ApiTokenPermission]
    # filter_backends = (filters.DjangoFilterBackend,)
    # queryset = Event.objects.all()
    # filterset_fields = ('category', 'in_stock')
    # filterset_class = EventFilter
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ['title']

    def get(self, request):
        page = request.GET.get('page', 1)
        events_data = EventFilter(request.GET, queryset=Event.objects.all().order_by('-creation_date')).qs
        # filter_data = {"categories": request.GET.get('categories').split(',')
        #                if isinstance(request.GET.get('categories', ""), str) and request.GET.get('categories') else [],
        #                "states": request.GET.get('states').split(',')
        #                if isinstance(request.GET.get('states', ""), str) and request.GET.get('states') else [],
        #                "cities": request.GET.get('cities', "").split(',')
        #                if isinstance(request.GET.get('cities', ""), str) and request.GET.get('cities') else [],
        #                "start_date": string_to_int(request.GET.get('start_date', "2")),
        #                "ticket_fee": string_to_int(request.GET.get('ticket_fee', "2")),
        #                "free": string_to_bool(request.GET.get('free', "False")),
        #                "is_responsible": string_to_bool(request.GET.get('is_responsible', "True"))}
        # data = EventFilterSerializer(data=filter_data)
        # if data.is_valid():
        # events_data = Event.objects.all()
            # if isinstance(data.validated_data['is_responsible'], bool):
            #     events_data = events_data.filter(Q(is_responsible=data.validated_data['is_responsible']))
            # if data.validated_data["free"]:
            #     events_data = events_data.filter(Q(ticket_fee=0))
            # elif data.validated_data["free"] == False:
            #     free_query = events_data.filter(Q(ticket_fee__gt=0))
            # if data.validated_data["categories"]:
            #     events_data = events_data.filter(Q(categories__name__in=data.validated_data["categories"]))
            # if data.validated_data["states"]:
            #     events_data = events_data.filter(Q(address__state__in=data.validated_data["states"]))
            # if data.validated_data["cities"]:
            #     events_data = events_data.filter(Q(address__city__in=data.validated_data["cities"]))
            # events_data = events_data.filter(Q(end_date__gte=get_current_time())).distinct()
            # if data.validated_data["start_date"] != 2:
            #     events_data = events_data.order_by("start_date") if \
            #         data.validated_data["start_date"] == 0 else events_data.order_by("-start_date")
            # if data.validated_data["ticket_fee"] != 2:
            #     events_data = events_data.order_by("ticket_fee") if \
            #         data.validated_data["ticket_fee"] == 0 else events_data.order_by("-ticket_fee")
        paginator = Paginator(events_data, settings.PAGE_SIZE)
            # if int(page) > events_data.num_pages or int(page) < 1:
            #     raise NotFound
        try:
            events_data = paginator.page(page)
        except PageNotAnInteger:
            events_data = paginator.page(1)
            page = 1
        except EmptyPage:
            events_data = paginator.page(paginator.num_pages)
            page = paginator.num_pages
        return response(data={"events": [i.serialize(extra_info=True) for i in events_data],
                            "current_page": page,
                            "last_page": paginator.num_pages,
                            "has_next": events_data.has_next(),
                            "has_previous": events_data.has_previous()})
        # raise ValidationError(error_list=error_many_list_serializer(data.errors))

class EventView(APIView):
    permission_classes = []


    def post(self, request, public_id=None):
        data = EventCreateSerializer(data=request.data)
        if data.is_valid():
            if data.validated_data.get('ticket_fee') == 0:
                try:
                    charge = stripe.Charge.create(amount=settings.FREE_EVENT_CHARGE,
                                                  currency="amd", source=request.user.stripe_id)
                except Exception as e:
                    raise StripeError()
            event = data.create(data.validated_data)
            event.host = request.user
            event.available_places = event.ticket_amount
            event.save()
            if event.ticket_fee == 0:
                Payment.objects.create(
                    end_time=get_current_time(),
                    amount=settings.FREE_EVENT_CHARGE,
                    event=event,
                    user = request.user,
                    reason = 1,
                    refund_id = charge['id']
                )
            return response(data=event.serialize(extra_info=True))
        # errors.update(data.errors)
        raise ValidationError(error_list=error_many_list_serializer(data.errors))

    def get(self, request, public_id=None):
        page = request.GET.get('page', 1)
        user = request.user
        if public_id is None:
            events_data = Event.objects.filter(host=user)
            if not events_data:
                if request.user.is_company:
                    events_data = Event.objects.filter(users=user)
                else:
                    events_data = Event.objects.filter(id__in=Subquery(Ticket.objects.filter(user=user).values('event__id')))
                if not events_data:
                    raise UserHasNoEvent()
            events_data = EventFilter(request.GET, events_data.order_by('-creation_date')).qs
            if events_data is not None:
                paginator = Paginator(events_data, settings.PAGE_SIZE)
                # if int(page) > events_data.num_pages or int(page) < 1:
                #     raise NotFound
                try:
                    events_data = paginator.page(page)
                except PageNotAnInteger:
                    events_data = paginator.page(1)
                    page = 1
                except EmptyPage:
                    events_data = paginator.page(paginator.num_pages)
                    page = paginator.num_pages
                return response(data={"events": [i.serialize(extra_info=True) for i in events_data],
                                      "current_page": page,
                                      "last_page": paginator.num_pages,
                                      "has_next": events_data.has_next(),
                                      "has_previous": events_data.has_previous()})
        else:
            event = Event.objects.filter(public_id=public_id).first()
            if not event:
                raise EventNotFound
            return response(data=event.serialize(extra_info=True))


    def delete(self, request, public_id=None):
        if public_id:
            event = Event.objects.filter(public_id=public_id).first()
            if event:
                if Ticket.objects.filter(event=event):
                    if event.is_responsible:
                        try:
                            refund_all_event_users(event)
                        except NoPaymentIsMade as e:
                            pass
                        except StripeError() as e:
                            raise e
                    else:
                        raise CannotDeleteEventHavingTickets()
                event.delete()
                return response()
            raise EventNotFound
        raise NotFound


    def patch(self, request, public_id=None):
        if public_id:
            event = Event.objects.filter(public_id=public_id).first()
            if event:
                data = EventUpdateSerializer(data=request.data, event = event)
                if data.is_valid():
                    event = data.update(event, data.validated_data)
                    return response(data=event.serialize())
                raise ValidationError(error_list=error_many_list_serializer(data.errors))
            raise EventNotFound
        raise NotFound


    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [ApiTokenPermission, LoggedInPermission, UserVerified]
        elif self.request.method == 'POST':
            permission_classes = [ApiTokenPermission, LoggedInPermission, UserVerified, CompanyUserPermission]
        else:
            permission_classes = [ApiTokenPermission, LoggedInPermission, UserVerified, CompanyUserPermission,
                                  CompanyEventPossessionPermission]
        return [permission() for permission in permission_classes]



class EventCategory(APIView):
    permission_classes = [ApiTokenPermission, LoggedInPermission, UserVerified, CompanyUserPermission,
                          CompanyEventPossessionPermission]

    # add smth if company updates the event it has to be sent users as category.
    def patch(self, request, public_id):
        data = CategoryUserSerializer(data=request.data, event=request.event)
        if data.is_valid():
            data.update(request.event, data.validated_data)
            return response()
        raise ValidationError(error_list=error_many_list_serializer(data.errors))

    # def get(self, request, public_id):
    #     event = Event.objects.filter(public_id=public_id).first()
    #     if event:
    #         all_categories = event.categories.all()
    #         if all_categories is not None:
    #             return response(data={"categories": [i.serialize() for i in all_categories]})
    #         raise EventHasNoCategory()
    #     raise EventNotFound

    def delete(self, request, public_id):
        data = CategoryUserSerializer(data=request.data, event=request.event)
        if data.is_valid():
            data.remove(request.event, data.validated_data)
            return response()
        raise ValidationError(error_list=error_many_list_serializer(data.errors))



class EventAddress(APIView):
    permission_classes = [ApiTokenPermission, LoggedInPermission, UserVerified, CompanyUserPermission,
                          CompanyEventPossessionPermission]

    # def post(self, request, public_id):
    #     event=request.event
    #     data = AddressCreateSerializer(data=request.data)
    #     if data.is_valid():
    #         zip_code, hash = data.get_hash(data.validated_data)
    #         address = Address.objects.filter(hash=hash)
    #         if zip_code is not None:
    #             data.validated_data['zip_code'] = zip_code
    #         if not address:
    #             address = data.create(data.validated_data)
    #             event.address = address
    #             event.save()
    #             return response()
    #         raise EventHasAddress()
    #     raise ValidationError(error_list=error_many_list_serializer(data.errors))

    # todo check same for user and understand what to do if user changes
    def patch(self, request, public_id):
        event = request.event
        if not request.data:
            raise AddressDataNotValid()
        data = AddressSerializer(data=request.data)
        if data.is_valid():
            address = event.address
            if address:
                address_hash = data.get_hash(data.validated_data)
                found_address = Address.objects.filter(hash=address_hash).first()
                # todo find better solution of finding all relationships
                if not (CustomUser.objects.filter(address=address) and
                        Event.objects.filter(address=address).count() > 1):
                    data.update(address, data.validated_data)
                elif not found_address:
                    address = data.create(data.validated_data)
                else:
                    address = found_address
                event.address = address
                event.save()
                return response()
            raise EventHasNoAddress()
        raise ValidationError(error_list=error_many_list_serializer(data.errors))


    # def delete(self, request, public_id):
    #     event = request.event
    #     address = event.address
    #     if address:
    #         event.address = None
    #         event.save()
    #         if not (CustomUser.objects.filter(address=address) and
    #                     Event.objects.filter(address=address)):
    #             address.delete()
    #         return response()
    #     raise EventHasNoAddress()


class CoHostEventView(APIView):
    permission_classes = []

    def patch(self, request, public_id):
        event = request.event
        data = EventCompanyUser(data=request.data)
        if data.is_valid():
            data.update(event, data.validated_data)
            return response()
        raise ValidationError(error_list=error_many_list_serializer(data.errors))


    def delete(self, request, public_id):
        event = request.event
        data = EventCompanyUser(data=request.data)
        if data.is_valid():
            if data.user == request.user and not data.user == event.host:
                event.users.remove(data.user)
            raise UserPermission()
        raise ValidationError(error_list=error_many_list_serializer(data.errors))

    def get_permissions(self):
        if self.request.method == 'PATCH':
            permission_classes = [ApiTokenPermission, LoggedInPermission, UserVerified, CompanyUserPermission,
                                  CompanyEventPossessionPermission]
        else:
            permission_classes = [ApiTokenPermission, LoggedInPermission, UserVerified, CompanyUserPermission,
                                  CompanyCoCompanyEventPossessionPermission]
        return [permission() for permission in permission_classes]


class EventTicketsView(APIView):
    permission_classes = []

    def get(self, request, public_id):
        page = request.GET.get('page', 1)
        event = Event.objects.filter(public_id=public_id).first()
        if not event:
            raise EventNotFound
        tickets = Ticket.objects.filter(event=event)
        tickets = TicketFilter(request.GET, queryset=tickets).qs
        paginator = Paginator(tickets, settings.TICKET_PAGE_SIZE)
        try:
            tickets = paginator.page(page)
        except PageNotAnInteger:
            tickets = paginator.page(1)
            page = 1
        except EmptyPage:
            tickets = paginator.page(paginator.num_pages)
            page = paginator.num_pages
        return response(data={"tickets": [i.serialize(extra_info=False) for i in tickets],
                              "current_page": page,
                              "last_page": paginator.num_pages,
                              "has_next": tickets.has_next(),
                              "has_previous": tickets.has_previous()})


    def post(self, request, public_id):
        event = Event.objects.filter(public_id=public_id).first()
        if not event:
            raise EventNotFound
        if event.ticket_fee == 0:
            data = FreeTicketCreateSerializer(data=request.data)
            if data.is_valid():
                if Ticket.objects.filter(user = request.user, event=event).count() + data.validated_data.get("quant") >TICKET_AMOUNT:
                    raise UserCanBuyAtMostFreeTickets(TICKET_AMOUNT)
                result = []
                email_result = []
                for i in range(0, data.validated_data.get("quant")):
                    ticket = Ticket.objects.create(user=request.user,
                                                    event=event,
                                                    is_vip=data.validated_data.get("is_vip"))
                    result.append(ticket.public_id)
                    email_result.append(ticket)
                send_celery_email('Bought Tickets', request.user.email, settings.TICKET_TEMPLATE,
                                                                                         email_result)
                return response(data=result)
            raise ValidationError(error_list=error_many_list_serializer(data.errors))
        raise UserPermission

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [ApiTokenPermission, LoggedInPermission, UserVerified, CompanyUserPermission,
                                  CompanyCoCompanyEventPossessionPermission]
        else:
            permission_classes = [ApiTokenPermission, LoggedInPermission, UserVerified]
        return [permission() for permission in permission_classes]

