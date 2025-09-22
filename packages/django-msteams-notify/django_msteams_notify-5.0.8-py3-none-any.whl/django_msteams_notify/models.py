import uuid
from django.db import models
from django_tenants.utils import get_current_schema

class TeamsNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")  

    def save(self, *args, **kwargs):
        if not self.schema_name:
            try:
                self.schema_name = get_current_schema()
            except Exception:
                self.schema_name = "public"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.schema_name}] {self.sent_at} - {self.status}"