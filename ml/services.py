import joblib
import requests

# fastapi 로 보낼 주소
fastapi_url = "http://127.0.0.1:8001/ml/fastapi/predict"

def predict_services(text: str, timeout: float=3.0):
    data = {"text": text}
    r = requests.post(fastapi_url, json=data, timeout=timeout)
    r.raise_for_status()
    return r.json()