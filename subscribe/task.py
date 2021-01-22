from datetime import datetime
from celery import shared_task
from celery.task import periodic_task
from authentication.utils import send_email, get_current_time
from celery.schedules import crontab
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django.conf import settings
from subscribe.models import Subscriber
from datetime import timedelta
from event_crud.models import Event
from user_crud.models import CustomUser

@shared_task
def send_celery_email(subject, to, template, value):
    return send_email(subject, to, template, value)


# @periodic_task(run_every=crontab(minute="*")) # It will run your task every minute
@shared_task
def send_subscription_emails():
    exp_day, exp_hour, exp_min, exp_sec = settings.CELERY_TASK_INTERVAL
    subscribers = Subscriber.objects.all()
    amount_of_events = 100
    events_array = []
    j=1
    user = None
    for i in subscribers:
        try:
            user = CustomUser.objects.get(email=i.email)
        except CustomUser.DoesNotExist or CustomUser.MultipleObjectsReturned:
            user = None
        print(i)
        # print(i.last_subscription_email_date)
        # print(get_current_time())
        # print(timedelta(days=exp_day, hours=exp_hour, minutes=exp_min, seconds=exp_sec))
        # print(bool(i.last_subscription_email_date > get_current_time() + timedelta(days=exp_day,
        #                                                             hours=exp_hour,
        #                                                             minutes=exp_min,
        #                                                             seconds=exp_sec)))
        if i.last_subscription_email_date < get_current_time() + timedelta(days=exp_day,
                                                                           hours=exp_hour,
                                                                           minutes=exp_min,
                                                                           seconds=exp_sec):
            # print("Get into first if")
            if user:
                if user.categories:
                    event_data = Event.objects.filter(categories__in = user.categories.all())
                if user.address:
                    events_data = events_data.filter(address__city__in =user.address.city,
                                                     address__state__in = user.address.state)
            elif not user or not events_data or events_data.count()<4:
                events_data = Event.objects.all()
            amount_of_events = events_data.count() if events_data.count()<100 else 100
            events_data = events_data.order_by('-creation_date')
            if j*4 > amount_of_events/4:
                j = 1
            events_array = [m.serialize() for m in events_data[(j-1)*4: j*4]]
            # print(events_array)
            # print(j)
            # print(amount_of_events)
            send_email('Updates', i.email, settings.SUBSCRIBE_TEMPLATE, events_array)
            i.last_subscription_email_date = get_current_time()
            i.amount_of_subscription_emails = i.amount_of_subscription_emails + 1
            i.save()
            j += 1
    return True


