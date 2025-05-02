from rest_framework import serializers
from users.models import User
from chat_messages.models import MessageStatus, Message
from chats.models import Chat, ChatParticipants
from files.models import File

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
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