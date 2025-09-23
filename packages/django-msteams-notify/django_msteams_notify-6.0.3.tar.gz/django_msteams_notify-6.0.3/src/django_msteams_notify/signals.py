from django.db.models.signals import post_save
from django.dispatch import receiver
from django_msteams_notify.models import TeamsNotification
from django_msteams_notify.notify import send_notification  # <-- import the helper

@receiver(post_save, sender=TeamsNotification)
def send_teams_notification(sender, instance, created, **kwargs):
    if created:
        send_notification(instance)
