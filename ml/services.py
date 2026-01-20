import joblib
import requests

from credits.services import credit_minus

# fastapi 로 보낼 주소
fastapi_url = "http://127.0.0.1:8001/ml/fastapi/predict"

def predict_services(*, user, text: str, timeout: float=3.0):
    data = {"text": text}
    r = requests.post(fastapi_url, json=data, timeout=timeout)
    r.raise_for_status()

    credit_minus(user=user)
    print(r.json())
    return r.json()