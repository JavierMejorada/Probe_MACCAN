from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    recipients = models.ManyToManyField(
        User,
        through="NotificationUser",
        related_name="notifications",
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["-created_at"],
                name="notification_created_idx"
            ),
        models.Index(
                fields=["is_deleted"],
                name="notification_deleted_idx"
            ),
        ]
        ordering = ["-created_at"]
        
    def __str__(self):  
        return self.title
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])
        
        
class NotificationUser(models.Model):
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="user_statuses",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notification_statuses",
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True) 
    
class Meta:
    unique_together = ("notification", "user")
    indexes = [
            models.Index(
                fields=["user", "is_read"],
                name="notif_user_read_idx",
            ),
             models.Index(
                fields=["user"],
                name="notif_user_idx"
            ),
        ]
    def __str__(self):
        status = "leída" if self.is_read else "no leída"
        return f"{self.user.username} – {self.notification.title} ({status})"