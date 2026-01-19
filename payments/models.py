from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

def uuid_32():
    return f"{timezone.now():%Y%m%d}_{uuid.uuid4().hex}"

class Toss(models.Model):
    paymentkey = models.CharField(max_length=200, unique=True, null=True, blank=True,)
    order_id = models.CharField(max_length=64, unique=True, default=uuid_32())
    order_name = models.CharField(max_length=100)
    amount = models.PositiveIntegerField(default=1)
    status = models.CharField(
    max_length=10,
    choices=[("READY","대기"),("DONE","완료"),("ABORTED","실패"),("CANCELED", "취소")],
    default="READY",)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="toss_orders",)
    
    def __str__(self):
        return f"{self.order_name} | {self.status} | {self.order_id} | {self.amount}"

    def success_status(self, paymentkey: str):
        self.status = "DONE"
        self.paymentkey = paymentkey
        self.save(update_fields=["status", "paymentkey"])