import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from auths.models import EmailVerificationCode, PasswordResetCode
from google.oauth2 import id_token
from google.auth.transport import requests


def generate_verification_code():
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_verification_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def send_verification_code(user):
    code = generate_verification_code()
    expires_time = timezone.now() + timedelta(minutes=10)

    EmailVerificationCode.objects.update_or_create(
        user=user,
        defaults={  
            "code_hash": hash_verification_code(code),
            "expires_at": expires_time,
        },
    )

    send_mail(
        subject="Airport DRF | Email verification",
        message=(
            f"Hello {user.username},\n\n"
            f"Your verification code is: {code}\n\n"
            f"This code expires in 10 minutes ({expires_time.strftime("%d.%m.%Y %H:%M:%S")})"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

def verify_google_token(token):
    return id_token.verify_oauth2_token(
        token,
        requests.Request(),
        settings.GOOGLE_CLIENT_ID,
    )

def send_password_reset_code(user):
    code = generate_verification_code()
    expires_time = timezone.now() + timedelta(minutes=3)

    PasswordResetCode.objects.update_or_create(
        user=user,
        defaults={  
            "code_hash": hash_verification_code(code),
            "expires_at": expires_time,
        },
    )

    send_mail(
        subject="Airport DRF | Password Reset",
        message=(
            f"Hello {user.username},\n\n"
            f"Your verification code to reset password is: {code}\n\n"
            f"This code expires in 3 minutes ({expires_time.strftime("%d.%m.%Y %H:%M:%S")})"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )