from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from .models import CreditWallet, CreditLedger
from django.utils import timezone
import uuid

# 회원가입 시 credit wallet 생성
def create_credit_wallet(*, user):
    CreditWallet.objects.create(
        user=user
    )

# 결제 서비스 함수
def credit_services(*, user, amount: int, paymentkey: str, order_id: str):
    """
    결제 서비스 함수
    트랜잭션 적용
    """
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

# 크레딧 차감
def credit_minus(*, user, minus: int=(-1)):
    """
    크레딧 차감 서비스 함수
    uuid로 멱등성 키 unique 보장
    트랜잭션 적용
    """
    idempotency_key = f"{timezone.now():%Y%m%d}_{uuid.uuid4()}"
    with transaction.atomic():
        wallet = CreditWallet.objects.select_for_update().get(user=user)
        if wallet.credit < 0:
            raise ValidationError("크레딧이 부족합니다")
        
        CreditLedger.objects.create(
            wallet=wallet,
            growh=minus,
            reason="머신러닝 사용",
            idempotency_key=idempotency_key
        )

        CreditWallet.objects.filter(pk=wallet.pk).update(credit=F("credit") + minus)

        wallet.refresh_from_db()