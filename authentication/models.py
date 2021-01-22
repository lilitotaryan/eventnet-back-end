from datetime import timedelta

from django.db import models
from authentication.utils import get_current_time
from main_app.constants import SESSION_EXPIRATION_TIME
from user_crud.models import CustomUser


class Session(models.Model):
    token = models.CharField(max_length=50, unique=True, blank=False)
    user = models.ForeignKey(CustomUser, models.CASCADE, null=True)
    device_brand = models.CharField(max_length=200, blank=True, default=None)
    os_system = models.CharField(max_length=200, blank=False, default=None)
    disconnected_date = models.DateTimeField(default=get_current_time)
    connected_date = models.DateTimeField(default=get_current_time)
    is_expired = models.BooleanField(default=False)


    # Todo check for
    def is_unexpired(self):
        exp_day, exp_hour, exp_min, exp_sec = SESSION_EXPIRATION_TIME
        if self.is_expired:
            return False
        if get_current_time() <= self.connected_date + timedelta(days=exp_day,
                                                                 hours=exp_hour,
                                                                 minutes=exp_min,
                                                                 seconds=exp_sec):
            return True
        self.is_expired = True
        self.disconnected_date = get_current_time()
        self.save()
        return False

    def expire_session(self):
        self.is_expired = True
        self.disconnected_date = get_current_time()
        self.save()

    @classmethod
    def expire_all_sessions(cls, user):
        sessions = Session.objects.filter(is_expired=False, user=user)
        if sessions:
            [i.expire_session() for i in sessions]
