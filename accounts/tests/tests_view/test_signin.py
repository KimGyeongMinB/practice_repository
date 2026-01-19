from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class SigninTestCase(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.email = "pigking41@gmail.com"
        self.password = "test123@"
        self.nickname = "테스트닉네임실험"

        User.objects.create_user(
            email=self.email,
            password="test123@",
            nickname=self.nickname
        )

        self.signin_url = reverse("accounts:token_obtain_pair")

    def test_signin(self):
        signin = self.client.post(
            self.signin_url,
            {
                "email": self.email,
                "password": self.password,
                "nickname": self.nickname
            }
        )
        self.assertEqual(signin.status_code, 200)