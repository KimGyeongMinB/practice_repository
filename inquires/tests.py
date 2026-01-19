from rest_framework.test import force_authenticate, APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from inquires.models import Inquiry
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

# Create your tests here.
class InquiryTest(APITestCase):

    # 유저
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="user@test.com",
            password="pass1234!",
            nickname="user1",
        )
        cls.other = User.objects.create_user(
            email="other@test.com",
            password="pass1234!",
            nickname="other1",
        )

    # setup
    def setUp(self):
        self.client = APIClient()
        self.inquiry = Inquiry.objects.create(
        title="t1",
        content="c1",
        author=self.user,
    )
        self.inquiry_list_create_url = reverse("inquires:inquiry_list")
        self.inquiry_retrieve_update_delte = reverse("inquires:retrieve_update_delete", args=[self.inquiry.pk])
        self.inquiry_restore_list = reverse("inquires:restore_list")
        self.inquiry_restore = reverse("inquires:restore", args=[self.inquiry.pk])

    # 인증테스트
    def auth(self, user):
        self.client.force_authenticate(user=user)
    
    # 리스트
    def test_list(self):
        self.inquiry.soft_delete()

        res = self.client.get(self.inquiry_list_create_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # 생성
    def test_create(self):
        self.auth(self.user)
        data = {"title":"test", "content":"testcontent"}
        res = self.client.post(self.inquiry_list_create_url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    # 상세페이지
    def test_retrieve(self):
        self.auth(self.user)
        res = self.client.get(self.inquiry_retrieve_update_delte)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # 상세페이지 업데이트
    def test_retrieve_update(self):
        # 유저 정보가 다를때 실패
        self.client.force_authenticate(user=self.other)
        res_update_fail = self.client.patch(self.inquiry_retrieve_update_delte, data={"title":"유저정보다름", "content":"유저정보다름"}, format='json')
        self.assertEqual(res_update_fail.status_code, status.HTTP_403_FORBIDDEN)

        # 유저 정보가 같을때 성공
        self.client.force_authenticate(user=self.user)
        res_update_success = self.client.patch(self.inquiry_retrieve_update_delte, data={"title":"수정", "content":"수정"}, format='json')
        self.assertEqual(res_update_success.status_code, status.HTTP_200_OK)

    # 삭제
    def test_retrieve_delete(self):
        self.client.force_authenticate(user=self.user)
        res_delete = self.client.delete(self.inquiry_retrieve_update_delte)
        self.assertEqual(res_delete.status_code, status.HTTP_204_NO_CONTENT)

        # 즉각적으로 db 반영
        self.inquiry.refresh_from_db()
        self.assertTrue(self.inquiry.is_delete)
        self.assertIsNotNone(self.inquiry.deleted_at)
        
        # 유저 다를때 실패
        self.client.force_authenticate(user=self.other)
        res_delete = self.client.delete(self.inquiry_retrieve_update_delte)
        self.assertEqual(res_delete.status_code, status.HTTP_403_FORBIDDEN)

    # 복구 가능한 리스트(3일이 안 지난 문의)
    def test_restore_list(self):
        self.inquiry.is_delete = True
        self.inquiry.deleted_at = timezone.now() - timedelta(days=2)
        self.inquiry.save(update_fields=["is_delete", "deleted_at"])

        self.auth(self.user)
        res = self.client.get(self.inquiry_restore_list)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # 복구
    def test_restore(self):
        self.inquiry.soft_delete()
        self.auth(self.user)
        res = self.client.post(self.inquiry_restore)
        self.assertEqual(res.status_code, status.HTTP_200_OK)