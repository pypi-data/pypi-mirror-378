from django_tenants.utils import get_tenant

@receiver(post_save, sender=TeamsNotification)
def send_notification_signal(sender, instance, created, **kwargs):
    if created:
        tenant = get_tenant(instance)  
        send_teams_message_task.delay(str(instance.id), tenant.schema_name)
