from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import PredictSerializer
from .services import predict_services

# 어디 내원해야 하는지
medicine = {
    17:"내과",
    14:"산부인과",
    15:"소아청소년과",
    16:"응급의학과"
}

class PredictAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PredictSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user=request.user
            serializer.save(user=user)
            predict = predict_services(user=user, text=serializer.validated_data["text"])

        return Response({"결과": medicine[predict['predict_result']]})