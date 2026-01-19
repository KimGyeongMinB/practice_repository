from django.contrib import admin
from .models import Toss

@admin.register(Toss)
class TossAdmin(admin.ModelAdmin):
    list_display = ("order_id", "paymentkey", "amount")
