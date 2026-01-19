from django.utils import timezone 
from django.db import models
from django.conf import settings
from datetime import timedelta
from django.db.models import Q

User = settings.AUTH_USER_MODEL

class InquiryQuerySet(models.QuerySet):
    def alive_list(self):
        return self.filter(is_delete=False)

    def delete_list(self, user: str):
        return self.filter(is_delete=True, author=user)
    
    def search(self, keyword, title_only=False, author_only=False):
        if not keyword:
            return self
        
        if title_only:
            return self.filter(title__icontains=keyword)
        
        if author_only:
            return self.filter(author__nickname__icontains=keyword)
        
        return self.filter(
            Q(title__icontains=keyword) |
            Q(content__icontains=keyword) |
            Q(author__nickname__icontains=keyword)
        )

# 문의사항
class Inquiry(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inquiry")
    is_delete = models.BooleanField(default=False)

    deleted_at = models.DateTimeField(null=True, blank=True)
    hard_deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = InquiryQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at", "created_at", "author", "title"]
        indexes=[
            models.Index(fields=["-created_at", "created_at", "author", "title"])
        ]

    def __str__(self):
        return f"{self.title} | {self.content} | {self.author}"
    
    # 소프트 삭제
    def soft_delete(self):
        self.is_delete = True
        self.deleted_at = timezone.now()
        self.hard_deleted_at = self.deleted_at + timedelta(days=3)
        self.save(update_fields=["is_delete", "deleted_at", "hard_deleted_at"])

    # 복구
    def restore(self):
        self.is_delete = False
        self.deleted_at = None
        self.hard_deleted_at = None
        self.save(update_fields=["is_delete", "deleted_at", "hard_deleted_at"])


    # 3일 지났는지 확인용 메서드
    def restore_deadline(self):
        if self.deleted_at == None:
            return None
        return self.deleted_at + timedelta(days=3)
    
    # 복구 가능한지 확인하는 메서드
    def can_restore(self):
        if not self.is_delete or not self.deleted_at:
            return None
        return timezone.now() <= self.restore_deadline()

class InquiryImage(models.Model):
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='image')
    image = models.ImageField(upload_to="sample/%Y/%m/%d/", blank=True, null=True)

    def __str__(self) -> str:
        return self.inquiry