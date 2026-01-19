from django.urls import path
from .views import (SignupAPIView, CustomTokenObtainPairView, 
                    SignupConfirmAPIView, LogoutAPIView, MyPageAPIView, ForgotPasswordAPIView,
                    VerifyPasswordAPIView, ResetPasswordAPIView)
from rest_framework_simplejwt.views import (
    TokenRefreshView,    # 토큰 갱신
)

app_name = 'accounts'

urlpatterns = [
    path("signup-email/", SignupAPIView.as_view(), name='signup_email'),
    path("signup-verify/", SignupConfirmAPIView.as_view(), name='signup_verify'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("mypage/<str:nickname>/", MyPageAPIView.as_view(), name="mypage"),
    path("forgot-password/", ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path("verify-password/", VerifyPasswordAPIView.as_view(), name='verify_password'),
    path("reset-password/", ResetPasswordAPIView.as_view(), name='reset_password')
]