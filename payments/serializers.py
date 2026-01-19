# payments/serializers.py
from .models import Toss
from rest_framework import serializers

class TossConfirmSerializer(serializers.Serializer):
    paymentkey = serializers.CharField()
    order_id = serializers.CharField()
    amount = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        order_id = attrs["order_id"]
        amount = attrs["amount"]

        order = Toss.objects.filter(order_id=order_id, status="READY").first()
        if not order:
            raise serializers.ValidationError({"order_id": "READY 상태의 주문이 없습니다."})

        if order.amount != amount:
            raise serializers.ValidationError({"amount": "주문 금액이 일치하지 않습니다."})

        self.instance = order
        return attrs


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Toss
        fields = ("amount", "order_name")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("amount는 1 이상이어야 합니다.")
        return value