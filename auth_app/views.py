from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str
from .models import EmailVerification, PasswordResetToken, TwoFactorAuth
from .serializers import (
    UserRegisterSerializer,
    CustomTokenObtainPairSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    TwoFactorOTPSerializer,
    TwoFactorVerifySerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordChangeSerializer
)
from .utils import (
    send_verification_email,
    send_password_reset_email,
    send_otp_email
)
import pyotp

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        send_verification_email(self.request, user)

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # In a real implementation, you would add the token to a blacklist
        return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)

class VerifyEmailView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        
        user = get_object_or_404(User, email=email)
        
        if user.is_verified:
            return Response({"detail": "Email is already verified"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP (implementation depends on your OTP system)
        if verify_otp(user, otp):  # You need to implement this function
            user.is_verified = True
            user.save()
            return Response({"detail": "Email successfully verified"})
        
        return Response({"detail": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

class ResendVerificationView(generics.GenericAPIView):
    serializer_class = ResendVerificationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = get_object_or_404(User, email=email)
        
        if user.is_verified:
            return Response({"detail": "Email is already verified"}, status=status.HTTP_400_BAD_REQUEST)
        
        send_verification_email(request, user)
        return Response({"detail": "Verification email resent"})

class TwoFactorSendOTPView(generics.GenericAPIView):
    serializer_class = TwoFactorOTPSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = get_object_or_404(User, email=email)
        
        two_fa, _ = TwoFactorAuth.objects.get_or_create(user=user)
        otp = two_fa.generate_otp()
        
        send_otp_email(user.email, otp)
        return Response({"detail": "OTP sent to email"})

class TwoFactorVerifyOTPView(generics.GenericAPIView):
    serializer_class = TwoFactorVerifySerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        
        user = get_object_or_404(User, email=email)
        two_fa = get_object_or_404(TwoFactorAuth, user=user)
        
        if two_fa.verify_otp(otp):
            two_fa.last_used = timezone.now()
            two_fa.save()
            return Response({"detail": "OTP verified successfully"})
        
        return Response({"detail": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

class TwoFactorEnableView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        two_fa, _ = TwoFactorAuth.objects.get_or_create(user=user)
        two_fa.is_enabled = True
        two_fa.save()
        return Response({"detail": "2FA enabled successfully"})

class TwoFactorDisableView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        two_fa = get_object_or_404(TwoFactorAuth, user=user)
        two_fa.is_enabled = False
        two_fa.save()
        return Response({"detail": "2FA disabled successfully"})

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = get_object_or_404(User, email=email)
        
        send_password_reset_email(request, user)
        return Response({"detail": "Password reset link sent to email"})

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            uid = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        
        if user is not None and PasswordResetToken.objects.filter(user=user, token=token, is_used=False).exists():
            user.set_password(new_password)
            user.save()
            PasswordResetToken.objects.filter(user=user, token=token).update(is_used=True)
            return Response({"detail": "Password has been reset successfully"})
        
        return Response({"detail": "Invalid reset link"}, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        if not user.check_password(old_password):
            return Response({"detail": "Wrong password"}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password updated successfully"})