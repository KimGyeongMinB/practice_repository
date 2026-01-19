from typing import Any
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
from inquires.models import Inquiry

class Command(BaseCommand):
    help = "문의사항 하드삭제"

    def handle(self, *args: Any, **options: Any) -> str | None:
        hard_time = timezone.now() - timedelta(days=3)
        qs =  Inquiry.objects.filter(is_delete=True, deleted_at__lt=hard_time)

        qs_count = qs.count()

        qs.delete()

        self.stdout.write(
            self.style.SUCCESS(f'하드삭제 성공, {qs_count} 개 삭제')
        )