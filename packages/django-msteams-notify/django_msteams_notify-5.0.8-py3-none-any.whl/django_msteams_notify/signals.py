from django.db.models.signals import post_save
from django.dispatch import receiver
from django_msteams_notify.models import TeamsNotification
from django_msteams_notify.tasks import send_teams_notification_task


@receiver(post_save, sender=TeamsNotification)
def send_notification_signal(sender, instance, created, **kwargs):
    if created:
        send_teams_notification_task.delay(str(instance.id), instance.schema_name)
