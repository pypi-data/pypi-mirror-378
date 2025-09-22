from celery import shared_task
from django_tenants.utils import schema_context
from django_msteams_notify.models import TeamsNotification
from django_msteams_notify.utils import send_teams_message

@shared_task(bind=True, max_retries=3)
def send_teams_message_task(self, notification_id, schema_name="public"):
    with schema_context(schema_name):
        try:
            notification = TeamsNotification.objects.get(id=notification_id)
            send_teams_message(notification)
        except TeamsNotification.DoesNotExist:
            return False
        except Exception as exc:
            raise self.retry(exc=exc, countdown=60)
    return True
