import time
import requests
from django.conf import settings
from django_msteams_notify.models import TeamsNotification

def send_teams_message(notification: TeamsNotification, retries=3, delay=5):
    """
    Send a Teams message and update notification status.
    Retries if network or Teams fails.
    """
    webhook_url = getattr(settings, "TEAMS_WEBHOOK_URL", None)
    if not webhook_url:
        notification.status = "failed"
        notification.save(update_fields=["status"])
        return False

    for attempt in range(1, retries + 1):
        try:
            payload = {"text": notification.message}
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 200:
                notification.status = "sent"
                notification.save(update_fields=["status"])
                return True
            else:
                print(f"Attempt {attempt}: Teams returned status {response.status_code}")
        except Exception as exc:
            print(f"Attempt {attempt} exception: {exc}")
        time.sleep(delay)

    notification.status = "failed"
    notification.save(update_fields=["status"])
    print("All retries failed, notification not sent")
    return False
