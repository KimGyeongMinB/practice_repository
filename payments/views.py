from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import TossConfirmSerializer, OrderCreateSerializer
from .services import toss_services
from rest_framework import status
from django.db import transaction
from .models import Toss
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from credits.services import credit_services

User = get_user_model()

def pay_page(request):
    return render(request, "payments/pay.html")

class OrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=request.user)

        return Response(
            {
                "order_id": order.order_id,
                "paymentkey": order.paymentkey,
                "amount": order.amount,
                "orderName": order.order_name,
            },
            status=status.HTTP_201_CREATED,
        )

# 토스 승인
class TossConfirmAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TossConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.instance

        payment_result = toss_services(
            paymentkey=serializer.validated_data["paymentkey"],
            order_id=order.order_id,
            amount=order.amount
        )

        with transaction.atomic():
            tran_order = Toss.objects.select_for_update().get(order_id=order.order_id)

            if tran_order.status == "DONE":
                return Response(payment_result, status=status.HTTP_200_OK)
            tran_order.success_status(serializer.validated_data["paymentkey"])

            credit_services(
                user=tran_order.user,
                amount=tran_order.amount,
                paymentkey=tran_order.paymentkey,
                order_id=tran_order.order_id
            )
        return Response(payment_result, status=status.HTTP_200_OK)