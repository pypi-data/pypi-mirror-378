from celery import shared_task
from django_msteams_notify.models import TeamsNotification
from django.core.exceptions import ObjectDoesNotExist
from django_msteams_notify.utils import send_teams_message

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_teams_notification_task(self, notification_id):
    try:
        notification = TeamsNotification.objects.get(id=notification_id)
        success = send_teams_message(notification)
        return success
    except ObjectDoesNotExist:
        # Don’t retry if the record never existed
        return False
    except Exception as e:
        raise self.retry(exc=e)
