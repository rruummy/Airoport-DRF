from django.db import models
from django.conf import settings

class EmailVerificationCode(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_verification",
    )

    code_hash = models.CharField(max_length=64)

    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Verification code for {self.user.email}"
