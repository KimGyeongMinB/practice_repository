from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenBlacklistView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken


# 앱에서 임포트
from .serializers import (SignupSerializer, TokenObtainPairSerializer, 
                        SignupEmailVerifySerializer, EmailCodeVerifySerializer,
                        MypageSerializer, ForgotPassword, VerifyForgotPassword, ResetPassword)
from .emails import signup_send_mail, random_code, forgot_password_send_mail
from .services import login_fail, clear_login_block_cache, login_block

User = get_user_model()

"""
SignupAPIView: 회원가입 시 이메일 발송
SignupConfirmAPIView: 발송받은 이메일, 코드 입력
"""
class SignupAPIView(APIView):
    """
    회원가입 시 이메일 인증
    이메일, 닉네임 입력후 이메일 인증
    """
    def post(self, request):
        serializer = SignupEmailVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 검증된 값
        email = serializer.validated_data["email"]
        nickname = serializer.validated_data["nickname"]

        code = random_code()
        signup_send_mail(
            recipient_list=[email],
            code=code
        )

        # 캐시 저장
        cache.set(
            key=f"signup_data:{email}",
            value={
                "nickname": nickname,
                "code": code,
            },
            timeout=300 # 5분
        )

        return Response(
            {"message": "이메일 인증 코드가 발송되었습니다."},
            status=200,
        )

class SignupConfirmAPIView(APIView):
    """
    이메일, 받은 인증코드, 비밀번호 입력
    비밀번호 입력은 SignupSerializer 에서 검증
    """
    def post(self, request):
        # 이메일 , 코드 인증
        email_validate = EmailCodeVerifySerializer(data=request.data)
        email_validate.is_valid(raise_exception=True)

        # 데이터 가져오기
        email = email_validate.validated_data["email"]
        signup_data = email_validate.validated_data["signup_data"]

        # 회원가입 모델시리얼라이저에 값 보내기
        user_data = {
            "email": email,
            "password": request.data.get("password"),
            "nickname": signup_data["nickname"],
        }

        signup = SignupSerializer(data=user_data)
        if signup.is_valid(raise_exception=True):
            user = signup.save()
            cache.delete(f"signup_data:{email}")
            
            return Response(
            {"id": user.id, "email": user.email, "nickname": user.nickname},
            status=status.HTTP_201_CREATED
        )

"""
xss 방지를 위해 httponly 사용
TokenObtainPairView 커스텀
"""
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        # 유저가 잘못된 이메일로 로그인 할시 DB 에 존재하지 않으면 count 안되게
        # 부모 클래스의 post 를 가져다 사용
        # 로그인 실패 후 5회 이내 성공시 캐시에 저장되어있던 실패 횟수 초기화
        email = request.data.get("email")
        if not User.objects.filter(email=email).exists():
            return Response(f"존재하지 않은 이메일 : {email}")

        try:
            response = super().post(request, *args, **kwargs)
            clear_login_block_cache(email)
        except:
            # login_block == 차단된 계정
            # login_fail ==  실패 횟수
            login_block(request)
            login_fail(request)
            raise
        
        if response.data['access']:
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=response.data['access'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                path="/"
                )
            response.data.pop('access')
        if response.data['refresh']:
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                value=response.data['refresh'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                path='/'
                )
            response.data.pop('refresh')

        return response

"""
LogoutAPIView : 로그아웃
리프레시 토큰 쿠키에서 불러오기
리프레시 토큰이 존재할 경우 
from rest_framework_simplejwt.tokens import RefreshToken 에서 불러와서 토큰 블랙리스트 처리
이후 쿠키에 있는 토큰 삭제
"""
class LogoutAPIView(TokenBlacklistView):
    permission_classes = [AllowAny]

    def post(self, request: Response, *args, **kwargs) -> Response:
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"], '토큰이 존재하지 않음')

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except:
                pass

        res = Response({"detail": "로그아웃 성공"}, status= status.HTTP_200_OK)
        res.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"])
        res.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE"])

        return res

"""
MyPageAPIView: 마이페이지
유저 정보(닉네임, 이메일), 내가 쓴 문의, 내 크레딧
"""
# 마이페이지
class MyPageAPIView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request, nickname):
        user = get_object_or_404(User, nickname=nickname)
        if user != request.user:
            return Response({"detail": "본인만 조회할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = MypageSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


"""
ForgotPasswordAPIView : 비밀번호 잊어버렸을때 이메일 입력후 발송
VerifyPasswordAPIView : 발송받은 이메일, 코드 입력
ResetPasswordAPIView : 이메일, 새 비밀번호, 확인용 새 비밀번호 입력
"""
class ForgotPasswordAPIView(APIView):
    authentication_classes = []

    def post(self, request):
        serializer = ForgotPassword(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        code = random_code()
        forgot_password_send_mail(
            recipient_list=[email],
            code=code
        )

        # 캐시 저장
        cache.set(
            key=f"forgot_password_data:{email}",
            value={
                "code": code,
            },
            timeout=300 # 5분
        )

        return Response(
            {"message": "이메일 인증 코드가 발송되었습니다."},
            status=200,
        )

class VerifyPasswordAPIView(APIView):
    authentication_classes = []

    def post(self, request):
        serializer = VerifyForgotPassword(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)

class ResetPasswordAPIView(APIView):
    authentication_classes = []

    def post(self, request):
        serializer = ResetPassword(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"mesage": "비밀번호 재설정을 완료했습니다."}, status=200)