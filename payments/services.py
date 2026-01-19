#payments/services.py
from dotenv import load_dotenv
import base64
import os
import requests

load_dotenv()

TOSS_CONFIRM_URL = "https://api.tosspayments.com/v1/payments/confirm"

def toss_services(*, paymentkey: str, order_id: str, amount: int):
    secret_key = os.getenv("TOSS_SECRET_KEY")
    encoding_secret_key = base64.b64encode(f"{secret_key}:".encode("utf-8")).decode()

    headers = {
        "Authorization": f"Basic {encoding_secret_key}",
        "Content-Type": "application/json",
    }

    # 모델 필드 그대로 키값으로 넣는게 아니라 토스페이 필드에 맞게 변경
    payload = {
        "paymentKey": paymentkey,
        "orderId": order_id,
        "amount": amount
    }

    res = requests.post(TOSS_CONFIRM_URL, headers=headers, json=payload)
    return res.json()