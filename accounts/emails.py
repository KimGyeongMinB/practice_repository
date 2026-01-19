from django.core.mail import send_mail
from django.conf import settings
import random
import secrets
import string

def random_code():
    return "".join(secrets.choice(string.digits) for _ in range(6))


def signup_send_mail(*, recipient_list: str, code: str):
    subject="회원가입 이메일 전송"
    message=f"인증코드는 {code} 입니다"
    from_email = settings.EMAIL_HOST_USER

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list = recipient_list
    )

def forgot_password_send_mail(*, recipient_list: str, code: str):
    subject="비밀번호 재설정 이메일 전송"
    message=f"인증코드는 {code} 입니다"
    from_email = settings.EMAIL_HOST_USER

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list = recipient_list
    )