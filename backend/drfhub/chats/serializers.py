from rest_framework import serializers

from .models import Chat, ChatParticipants
from chat_messages.models import Message
from chat_messages.serializers import MessageSerializer

class ParticipantSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.user_id')
    username = serializers.CharField(source='user.username')
    profile_pic = serializers.CharField(source='user.avatar')

    class Meta:
        model = ChatParticipants
        fields = ['user_id', 'username', 'profile_pic', 'joined_at']

class ChatSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(
        many=True,
        source='participants.all',
        read_only=True
    )
    last_message = serializers.SerializerMethodField()
    chat_name = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = [
            'chat_id',
            'is_group',
            'is_personal',
            'chat_name',
            'participants',
            'last_message',
            'created_at',
            'updated_at'
        ]

    def get_last_message(self, obj):
        if hasattr(obj, 'latest_messages') and obj.latest_messages:
            return MessageSerializer(obj.latest_messages[0]).data
        last_msg = Message.objects.filter(chat=obj).order_by('time_stamp').last()
        return MessageSerializer(last_msg).data if last_msg else None

    def get_chat_name(self, obj):
        if obj.is_personal:
            request_user = self.context.get('request_user')
            participants = obj.participants.exclude(user=request_user)
            return participants.first().user.username if participants.exists() else 'Deleted User'
        return obj.chat_name  # Add chat_name field if you want group names
    
    # def get_last_message(self, obj):
    #     # Uses prefetched messages
        # if hasattr(obj, 'latest_messages') and obj.latest_messages:
        #     return MessageSerializer(obj.latest_messages[0]).data
    #     return None