from django.db import models

from src.user.models import User


class Invitation(models.Model):
    id = models.AutoField(primary_key=True)
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invited_user')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invited_by_user')
    registered_at = models.DateTimeField(auto_now_add=True)
