from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Inquiry
from .serializers import InquirySerializer, InquiryRestoreSerializer
from rest_framework import permissions
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, FormParser

@extend_schema(
    summary="문의 목록/작성",
    description="GET: 삭제되지 않은 문의 목록 / POST: 문의 작성",
    tags=["Inquiry"],
)
# 문의사항 전체 조회, 작성
class InquiryListAPIView(ListCreateAPIView):
    serializer_class = InquirySerializer
    
    def get_queryset(self):
        qs = Inquiry.objects.alive_list()

        keyword = self.request.query_params.get("search", "")
        title_only = self.request.query_params.get("title_only")
        author_only = self.request.query_params.get("author_only")

        return qs.search(
            keyword,
            title_only=title_only,
            author_only=author_only
        )

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_authenticators(self):
        if self.request.method == "GET":
            return []
        return [JWTAuthentication()]
    
    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.author == request.user

@extend_schema(
    summary="내가 쓴 문의사항 수정, 상세, 삭제",
    description="GET: 내가 쓴 문의사항 상세페이지 / PATCH: 문의 수정 / DELETE: 문의 삭제(소프트삭제=3일뒤)",
    tags=["Inquiry"],
)
# 내가 쓴 문의사항 수정, 상세, 삭제
class InquiryRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer

    def perform_destroy(self, instance):
        return instance.soft_delete()


@extend_schema(
    summary="삭제한 자신의 문의사항 중 3일이 지나지 않은 조회 및 복구",
    description="GET: 자신이 삭제한 문의사항 조회 / POST: 복구 ",
    tags=["Inquiry"],
)
# 삭제한 문의사항 복구
class InquiryRestoration(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        inquiries = Inquiry.objects.delete_list(author=request.user)
        serializer = InquiryRestoreSerializer(inquiries, many=True)
        return Response(serializer.data)
    
    def post(self, request, pk):
        restore_inquiry = get_object_or_404(Inquiry, pk=pk, author=request.user, is_delete=True)

        if not restore_inquiry.can_restore():
            return Response({"detail": "복구 기간이 만료되었습니다."}, status=400)
        
        restore_inquiry.restore()
        return Response({"detail": "복구되었습니다."})