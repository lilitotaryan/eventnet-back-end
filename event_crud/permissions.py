from rest_framework import permissions

from main_app.api_exceptions import UserNotFound, EventNotFound, UserPermission
from .models import Event

class CompanyUserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_company:
            raise UserNotFound
        return True


class CompanyEventPossessionPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        public_id = view.kwargs.get('public_id', None)
        if public_id:
            event = Event.objects.filter(public_id=public_id).first()
            if not event:
                raise EventNotFound()
            # todo check this
            if not event.host == request.user:
                raise UserPermission()
            request.event = event
            return True
        raise EventNotFound()

class CompanyCoCompanyEventPossessionPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        public_id = view.kwargs.get('public_id', None)
        event = Event.objects.filter(public_id=public_id).first()
        if not event:
            raise EventNotFound()
        # todo check this
        if not event.host==request.user:
            if not event.users.filter(id=request.user.id).first()==request.user:
                raise UserPermission()
        request.event=event
        return True