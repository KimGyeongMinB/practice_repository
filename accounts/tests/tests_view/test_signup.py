from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from django.core.cache import cache

User = get_user_model()

class SignupTestCase(APITestCase):
    """
    회원가입 테스트, 메일전송
    """

    def setUp(self):
        self.client = APIClient()
        self.email = "pigking41@gmail.com"
        self.nickname = "테스트닉네임실험"
        self.signup_url = reverse("accounts:signupemail")
        self.verify_url = reverse("accounts:signupverify")

    def test_email_verify_success(self):
        email_post = self.client.post(
            self.signup_url,
            {
                "email": self.email,
                "nickname": self.nickname
            },
            format="json"
        )

        self.assertEqual(email_post.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

        # 캐시 가져오기
        code = cache.get(f"signup_data:{self.email}")
        self.assertIsNotNone(code['code'])


        verify_code = self.client.post(
            self.verify_url,
            {
                "email": self.email,
                "code": code['code'],
                "password": "test123@"
            },
            format="json"
        )
        print(f"베리파이 {verify_code}")
        self.assertEqual(verify_code.status_code, 201)