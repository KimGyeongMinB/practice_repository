from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

User = get_user_model()

class LogoutTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.email = "pigking41@gmail.com"
        self.password = "test123@"
        self.nickname = "테스트닉네임실험"

        user = User.objects.create_user(
            email=self.email,
            password=self.password,
            nickname=self.nickname
        )

        # 로그인 url
        self.logout_url = reverse("accounts:logout")

        # 리프레시 토큰 발급
        refresh = RefreshToken.for_user(user)

        # 문자열로 추출
        self.refresh_token = str(refresh)
        self.access_token = str(refresh.access_token)

        self.client.cookies[settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"]] = self.refresh_token
        self.client.cookies[settings.SIMPLE_JWT["AUTH_COOKIE"]] = self.access_token

    def test_logout(self):
        logout = self.client.post(self.logout_url)
        self.assertEqual(logout.status_code, 200)