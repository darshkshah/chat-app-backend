from rest_framework import serializers
from users.models import User
from chat_messages.models import MessageStatus, Message
from chats.models import Chat, ChatParticipants
from files.models import File

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'password',
            'last_login',
            'user_id',
            'first_name',
            'last_name',
            'username',
            'pn_country_code',
            'phone_number',
            'email',
            'bio',
            'online_status',
            'created_at',
            'is_active',
            'is_staff',
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            },
            'last_login': {
                'read_only': True
            },
            'is_active': {
                'read_only': True
            },
            'is_staff': {
                'read_only': True
            },
            'online_status': {
                'read_only': True
            },
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
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        
        # Update all other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()