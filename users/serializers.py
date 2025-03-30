from rest_framework import serializers
from .models import UserProfile, User
from .base_serializers import UserSerializer  # Changed import

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'user', 'full_name', 'avatar', 'bio', 'phone_number', 
            'birth_date', 'gender', 'address', 'city', 'country',
            'postal_code', 'website', 'matric_number', 'level',
            'program', 'show_email', 'show_phone'
        ]
        read_only_fields = ['user', 'full_name']

    def get_full_name(self, obj):
        return obj.full_name

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class AvatarUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['avatar']

class PublicUserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)
    bio = serializers.CharField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'full_name', 'avatar', 'bio', 'program'
        ]

    def get_full_name(self, obj):
        return obj.full_name