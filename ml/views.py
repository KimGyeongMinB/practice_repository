from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import PredictSerializer
from .services import predict_services

# Create your views here.
class PredictAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PredictSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        predict = predict_services(text=serializer.validated_data["text"])
        return Response({"결과": predict})