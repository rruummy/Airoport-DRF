from celery import shared_task
from django.utils import timezone

from emails.models import EmailVerificationCode, PasswordResetCode


@shared_task
def delete_email_expired_codes():
    deleted_count, _ = EmailVerificationCode.objects.filter(
        expires_at__lte=timezone.now()
    ).delete()

    print(f"Deleted {deleted_count} expired email verification codes.")

@shared_task
def delete_password_expired_codes():
    deleted_count, _ = PasswordResetCode.objects.filter(
        expires_at__lte=timezone.now()
    ).delete()

    print(f"Deleted {deleted_count} expired password reset codes.")