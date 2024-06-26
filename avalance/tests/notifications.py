from django.contrib.auth import user_logged_in
from django.dispatch import receiver

from tests.bot import send_message
from tests.exceptions import admin_notification

@receiver(user_logged_in)
def log_admin_login(sender, request, user, **kwargs):
    if request.path.startswith('/admin/'):
        admin_notification(message=f'someone entered the admin panel', request=request)


def notification_email_overflow(now):
    send_message(f'at {now} limit for sending password recovery messages has been reached')

