from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

# 유저 크레딧
class CreditWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    credit = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

class CreditLedger(models.Model):
    wallet = models.ForeignKey(CreditWallet, on_delete=models.CASCADE, related_name="ledgers")
    growh = models.IntegerField() # 증감
    reason = models.CharField(max_length=50) # 증감 이유
    provider = models.CharField(max_length=30, blank=True, default="") # 어디서 결제했는지
    credit_order_id = models.CharField(max_length=100)
    idempotency_key = models.CharField(max_length=250, unique=True) # 중복방지키
    created_at = models.DateTimeField(auto_now_add=True)