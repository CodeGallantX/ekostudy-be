from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import pyotp

User = get_user_model()

class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.expires_at

class TwoFactorAuth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=False)
    secret_key = models.CharField(max_length=32, blank=True)
    last_used = models.DateTimeField(null=True, blank=True)

    def generate_otp(self):
        if not self.secret_key:
            self.secret_key = pyotp.random_base32()
            self.save()
        totp = pyotp.TOTP(self.secret_key)
        return totp.now()

    def verify_otp(self, otp):
        if not self.secret_key:
            return False
        totp = pyotp.TOTP(self.secret_key)
        return totp.verify(otp, valid_window=1)