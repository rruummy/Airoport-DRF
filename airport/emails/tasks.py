from celery import shared_task
from django.utils import timezone

from emails.models import EmailVerificationCode, PasswordResetCode
from django.core.mail import send_mail
from django.conf import settings

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

@shared_task
def send_email_async(subject, message, recipient):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=False,
    )

@shared_task
def send_verification_email(email, code):
    send_mail(
        subject="Email verification",
        message=f"Your verification code is: {code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )