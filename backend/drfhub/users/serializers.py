from rest_framework import serializers

from chat_messages.models import MessageStatus, Message
from chats.models import Chat, ChatParticipants
from files.models import File

from .models import OTP, User
from .validators import phone_number_validator, country_code_validator, otp_validator

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'user_id',
            'first_name',
            'last_name',
            'phone_country_code',
            'phone_number',
            'username',
            'is_phone_verified',
            'email',
            'bio',
            'avatar',
            'online_status',
            'created_at',
            'is_active',
            'is_staff',
            'password',
            'last_login',
        )
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
            'last_login': {'read_only': True},
            'user_id': {'read_only': True},
            'is_active': {'read_only': True},
            'is_staff': {'read_only': True},
            'created_at': {'read_only': True},
            'is_phone_verified': {'read_only': True},
            'phone_number': {'read_only': True},
            'phone_country_code': {'read_only': True},
            'online_status': {'required': False},
            'avatar': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'username': {'required': False},
            'email': {'required': False},
            'bio': {'required': False},
        }

    def create(self, validated_data):
        # Extract password from validated_data
        password = validated_data.pop('password')
        
        # Create user instance without password
        user = User(**validated_data)
        
        # Set password properly using set_password method
        user.set_password(password)
        user.save()
        
        return user
        
    def update(self, instance, validated_data):
        # Handle password separately if it's being updated
        print("Update Method is being called.")
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        
        # Update all other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance

class SendOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, validators=[phone_number_validator], required=True)
    country_code = serializers.CharField(max_length=5, validators=[country_code_validator], required=True)

class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, validators=[phone_number_validator], required=True)
    country_code = serializers.CharField(max_length=5, validators=[country_code_validator], required=True)
    otp = serializers.CharField(max_length=6, required=True, validators=[otp_validator])

    def validate(self, data):
        phone_number = data.get('phone_number')
        country_code = data.get('country_code')
        otp = data.get('otp')

        try:
            otp_obj = OTP.objects.get(phone_number=phone_number, phone_country_code=country_code)
        except OTP.DoesNotExist:
            raise serializers.ValidationError({
                'phone_number': 'No matching phone number and country code found.'
            })

        if otp_obj.otp != otp:
            raise serializers.ValidationError({
                'otp': 'Incorrect OTP.'
            })

        return data

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()