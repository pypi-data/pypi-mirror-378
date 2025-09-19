import logging
import requests
from django.conf import settings
from django_msteams_notify.models import TeamsNotification

logger = logging.getLogger(__name__)

def send_teams_message(notification: TeamsNotification):
    """Send a Teams message and update notification status, with debug logging."""
    webhook_url = getattr(settings, "TEAMS_WEBHOOK_URL", None)

    if not webhook_url:
        logger.error("No TEAMS_WEBHOOK_URL configured in settings.")
        notification.status = "failed"
        notification.save(update_fields=["status"])
        return False

    try:
        payload = {"text": notification.message}
        response = requests.post(webhook_url, json=payload)

        if response.status_code == 200:
            notification.status = "sent"
            logger.info(f"✅ Teams message sent successfully for {notification.id}")
        else:
            notification.status = "failed"
            logger.error(
                f"❌ Teams webhook failed for {notification.id} "
                f"(status={response.status_code}): {response.text}"
            )

    except Exception as e:
        logger.exception(f"⚠️ Exception while sending Teams message {notification.id}: {e}")
        notification.status = "failed"

    notification.save(update_fields=["status"])
    return notification.status == "sent"
