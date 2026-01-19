from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL
# Create your models here.
class Predict(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="predict")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)