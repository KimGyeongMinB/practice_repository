from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from .models import CreditWallet, CreditLedger
from django.utils import timezone

def credit_services(*, user, amount: int, paymentkey: str, order_id: str):
    if amount <= 0:
        raise ValidationError("amount 는 1 이상이야 합니다.")
    
    if not paymentkey:
        raise ValidationError("paymentkey 가 있어야 합니다")
    
    if not order_id:
        raise ValidationError("order_id 가 있어야 합니다")
    
    # 멱등성 키
    idempotency_key = f"{timezone.now():%Y%m%d}_{paymentkey}"

    processed = CreditLedger.objects.filter(idempotency_key=idempotency_key).first()
    if processed:
        return processed
    
    with transaction.atomic():
        wallet,_ = CreditWallet.objects.select_for_update().get_or_create(user=user)

        ledger = CreditLedger.objects.create(
            wallet=wallet,
            growh=amount,
            reason="CHARGE",
            provider="TOSS",
            credit_order_id=order_id,
            idempotency_key=idempotency_key
        )

        CreditWallet.objects.filter(pk=wallet.pk).update(credit=F("credit") + amount)

        return ledger