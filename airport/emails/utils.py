from django.core.mail import send_mail
from django.conf import settings


def send_profile_update_email(user, changes):
    changes_text = "\n".join(
        f"{field}: {old} -> {new}"
        for field, (old, new) in changes.items()
    )

    send_mail(
        subject="Airport DRF | Profile updated",
        message=(
            f"Hello {user.username},\n\n"
            "Your profile has been successfully updated.\n\n"
            "Changed fields:\n"
            f"{changes_text}\n\n"
            "If you did not make these changes, please contact support."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    
def send_password_successfully_updated_email(user):
    send_mail(
        subject="Airport DRF | Password updated",
        message=(
            f"Hello {user.username},\n\n"
            "Your password was changed.\n\n"
            "If you did not make these changes, please contact support."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )