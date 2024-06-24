from datetime import timedelta

from django.contrib.auth import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

from tests.exceptions import admin_notification
from tests.models import EmailSent, EmailCooldownCounter
from tests.services import to_int


@receiver(user_logged_in)
def log_admin_login(sender, request, user, **kwargs):
    if request.path.startswith('/admin/'):
        admin_notification(message=f'someone entered the admin panel', request=request)


def can_send_email(user):
    if user.exists() is False:
        return False
    user = user.first()
    now = timezone.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    user_email_received = EmailSent.objects.filter(user=user, timestamp__gte=start_of_day).count()
    if user_email_received >= 3:
        return False

    last_counter = EmailCooldownCounter.objects.last()
    if (last_counter.cooldown - now) >= timedelta(hours=25):
        EmailSent.objects.create(user=user)
        EmailCooldownCounter.objects.create()
    elif 0 < to_int(last_counter.counter) <= 490:
        EmailSent.objects.create(user=user)
        last_counter.counter += 1
        last_counter.save()
        return True
    return False
