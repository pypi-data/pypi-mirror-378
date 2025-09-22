from django.db.models.signals import post_save
from django.dispatch import receiver
from django_msteams_notify.models import TeamsNotification
from django_msteams_notify.tasks import send_teams_message_task
from django_tenants.utils import get_current_tenant

@receiver(post_save, sender=TeamsNotification)
def send_notification_signal(sender, instance, created, **kwargs):
    if created:
        tenant = get_current_tenant()
        send_teams_notification_task.delay(tenant.schema_name, str(instance.id))
