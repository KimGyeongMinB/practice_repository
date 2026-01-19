from typing import Any
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.core.cache import cache
from inquires.serializers import InquirySimpleSerializer

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    """
    회원가입 시리얼라이저
    SignupConfirmAPIView 의 비밀번호 검증 및 해시, 생성
    """
    class Meta:
        model = User
        fields = ("nickname", "email", "password")

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("비밀번호를 입력해주세요.")
        if len(value) < 8:
            raise serializers.ValidationError("비밀번호는 8자 이상이어야 합니다.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            nickname=validated_data['nickname'],
            password=validated_data['password'],
            email=validated_data['email']
        )
        return user

# 회원가입시 이메일 필드 검증
class SignupEmailVerifySerializer(serializers.Serializer):
    """
    SignupAPIView 에서 입력한 이메일 및 닉네임 검증
    """
    nickname = serializers.CharField()
    email = serializers.EmailField()
    
    # 닉네임
    def validate_nickname(self, value):
        if len(value) > 15:
            raise serializers.ValidationError("닉네임은 15글자 이하로 설정해야 합니다.")
        
        if len(value) <= 2:
            raise serializers.ValidationError("닉네임은 3글자 이상로 설정해야 합니다.")
        
        if not value:
            raise serializers.ValidationError("닉네임을 입력해주세요.")
        
        return value
    
    # 이메일
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        
        if not value:
            raise serializers.ValidationError("이메일을 입력해주세요.")
        
        return value

# 이메일, 회원가입 토큰 검증
class EmailCodeVerifySerializer(serializers.Serializer):
    """
    이메일 인증코드 날라온것 검증
    """
    email = serializers.EmailField()
    code = serializers.CharField()

    # 이메일, 토큰 검증
    def validate(self, attrs):
        email = attrs["email"]
        code = attrs["code"]

        # 캐시에 저장된 이메일 가져오기
        cached = cache.get(f"signup_data:{email}")
        cached_code = cached.get("code")

        if not cached:
            raise serializers.ValidationError("인증 정보가 없거나 만료되었습니다. 다시 요청해주세요.")
        
        if code != cached_code:
            raise serializers.ValidationError("인증 코드가 올바르지 않습니다.")
        
        # 저장된 캐시도 같이 보내기
        attrs["signup_data"] = cached
        return attrs

# 로그인 커스텀
class TokenObtainPairSerializer(TokenObtainPairSerializer):
    
    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        data = super().validate(attrs)

        token = data['access']
        refresh = data['refresh']

        if not token or not refresh:
            raise AuthenticationFailed("인증 토큰이 누락되었습니다.")

        return {
            "access": token,
            "refresh": refresh
        }

# 마이페이지
class MypageSerializer(serializers.ModelSerializer):
    alive_inquiry = serializers.SerializerMethodField() # 문의
    delete_inquiry = serializers.SerializerMethodField() # 삭제한 문의
    wallet_credit = serializers.SerializerMethodField() # 크레딧

    class Meta:
        model = User
        fields = ("email", "nickname", "date_join", "alive_inquiry", "delete_inquiry", "wallet_credit")

    def get_alive_inquiry(self, obj):
        alive_inquiry = obj.inquiry.filter(is_delete=False)
        return InquirySimpleSerializer(alive_inquiry, many=True).data
    
    def get_delete_inquiry(self, obj):
        delete_inquiry = obj.inquiry.filter(is_delete=True)
        return InquirySimpleSerializer(delete_inquiry, many=True).data
    
    def get_wallet_credit(self, obj):
        wallet = obj.wallet
        return {
            "credit" : wallet.credit
        }

# 패스워드 잃어버렸을 경우 사용
class ForgotPassword(serializers.Serializer):
    email = serializers.EmailField()

    # 이메일 검증
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이메일이 존재하지 않습니다")
        
        if not value:
            raise serializers.ValidationError("이메일을 입력해주세요.")
        
        return value

class VerifyForgotPassword(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

        # 이메일, 토큰 검증
    def validate(self, attrs):
        email = attrs["email"]
        code = attrs["code"]

        # 캐시에 저장된 이메일 가져오기
        cached = cache.get(f"forgot_password_data:{email}")
        cached_code = cached.get("code")

        if not cached:
            raise serializers.ValidationError("인증 정보가 없거나 만료되었습니다. 다시 요청해주세요.")
        
        if code != cached_code:
            raise serializers.ValidationError("인증 코드가 올바르지 않습니다.")
        
        return attrs
    
    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        user.deactivate()

        cache.delete(f"forgot_password_data:{user.email}")
        return user

class ResetPassword(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField()
    recheck_new_password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs["email"]
        new_password = attrs["new_password"]
        recheck_new_password = attrs["recheck_new_password"]

        # 비밀번호 검증
        if not new_password or not recheck_new_password:
            raise serializers.ValidationError("비밀번호를 입력해주세요.")
        if len(new_password) < 8 or len(recheck_new_password) < 8:
            raise serializers.ValidationError("비밀번호는 8자 이상이어야 합니다.")
        if new_password != recheck_new_password:
            raise serializers.ValidationError("비밀번호가 같지 않습니다.")
        
        # 이메일 검증
        try:
            user = User.objects.get(email=email, is_active=False)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "비밀번호 재설정 인증이 완료되지 않았거나, 해당 사용자가 없습니다."})

        attrs["user"] = user
        return attrs
    
    def save(self):
        user = self.validated_data["user"]
        new_password = self.validated_data["new_password"]

        user.set_new_password(new_password)
        user.activate()

        return user