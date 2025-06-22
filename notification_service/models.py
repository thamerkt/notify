from django.db import models

# Create your models here.
class Notification(models.Model):
    user = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.title}"