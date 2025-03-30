from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from .models import EmailVerification, PasswordResetToken
from django.utils import timezone
from datetime import timedelta
import secrets

def send_verification_email(request, user):
    token = secrets.token_hex(32)
    expires_at = timezone.now() + timedelta(hours=24)
    
    EmailVerification.objects.create(
        user=user,
        token=token,
        expires_at=expires_at
    )
    
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}&email={user.email}"
    
    subject = "Verify Your Email Address"
    message = render_to_string('auth/email_verification.html', {
        'user': user,
        'verification_url': verification_url,
    })
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=message
    )

def send_password_reset_email(request, user):
    token = secrets.token_hex(32)
    expires_at = timezone.now() + timedelta(hours=1)
    
    PasswordResetToken.objects.create(
        user=user,
        token=token,
        expires_at=expires_at
    )
    
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}&uid={urlsafe_base64_encode(force_bytes(user.pk))}"
    
    subject = "Password Reset Request"
    message = render_to_string('auth/password_reset.html', {
        'user': user,
        'reset_url': reset_url,
    })
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=message
    )

def send_otp_email(email, otp):
    subject = "Your One-Time Password (OTP)"
    message = f"Your OTP is: {otp}"
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )

def verify_otp(user, otp):
    # Implement your OTP verification logic here
    # This could check against a stored OTP or use TOTP
    return True  # Placeholder