from rest_framework.authentication import BaseAuthentication, CSRFCheck
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings



class CustomJwtAuthentication(BaseAuthentication):

    def authenticate(self, request):
        
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])
        print(raw_token)
        if not raw_token:
            return None

        jwt_auth = JWTAuthentication()

        try:
            # JWTAuthentication().authenticate 에서 사용되는 함수 두개
            validated_token = jwt_auth.get_validated_token(raw_token)
            user = jwt_auth.get_user(validated_token)
        except (InvalidToken, TokenError):
            raise exceptions.AuthenticationFailed("유효하지 않은 토큰")
        except Exception:
            raise exceptions.AuthenticationFailed("인증 처리 중 오류")

        if user is None:
            raise exceptions.AuthenticationFailed("유저를 찾을수 없음")
        if not getattr(user, "is_active", True):
            raise exceptions.AuthenticationFailed("비활성화된 유저")

        # DRF 표준: (user, auth) 반환
        return (user, validated_token)