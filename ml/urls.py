from django.urls import path
from .views import PredictAPIView
app_name = 'ml'

urlpatterns = [
    path("predict-create/", PredictAPIView.as_view(), name="predict_create")
]