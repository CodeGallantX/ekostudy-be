from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    VerifyEmailView,
    ResendVerificationView,
    TwoFactorSendOTPView,
    TwoFactorVerifyOTPView,
    TwoFactorEnableView,
    TwoFactorDisableView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    PasswordChangeView
)

urlpatterns = [
    # Auth endpoints
    path('signup/', RegisterView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
    
    # 2FA endpoints
    path('2fa/send-otp/', TwoFactorSendOTPView.as_view(), name='2fa-send-otp'),
    path('2fa/verify-otp/', TwoFactorVerifyOTPView.as_view(), name='2fa-verify-otp'),
    path('2fa/enable/', TwoFactorEnableView.as_view(), name='2fa-enable'),
    path('2fa/disable/', TwoFactorDisableView.as_view(), name='2fa-disable'),
    
    # Password management
    path('password/forgot/', PasswordResetRequestView.as_view(), name='password-forgot'),
    path('password/reset/', PasswordResetConfirmView.as_view(), name='password-reset'),
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
]