from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI()

load_data = joblib.load("mldata/domain_pipeline.joblib")

# 스키마
class PredictModel(BaseModel):
    text: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/ml/fastapi/predict")
def text_predict(request: PredictModel):
    predict_result = load_data.predict([request.text])[0]
    return {"predict_result" : int(predict_result)}