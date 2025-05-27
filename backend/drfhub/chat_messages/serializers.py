from django.utils import timezone

from rest_framework import serializers

from chat_messages.models import Message, MessageStatus
from chats.models import Chat

class DateTimeRequestSerializer(serializers.Serializer):
    chat_id = serializers.IntegerField(
        min_value=0, 
        max_value=9223372036854775807, 
        required=True
    )
    timestamp = serializers.DateTimeField(
        input_formats=['iso-8601'],  # ISO format will handle timezone offsets
        required=False
    )
    def validate_chat_id(self, value):
        """
        Check that the chat exists.
        """
        try:
            Chat.objects.get(pk=value)
        except Chat.DoesNotExist:
            raise serializers.ValidationError(f"Chat with id {value} does not exist")
        return value
    


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            'message_id',
            'sender',
            'chat',
            'file',
            'time_stamp',
            'message',
            'is_file',
            'updated_at'
        )
        extra_kwargs = {
            'message_id': {
                'read_only': True
            },
            'time_stamp': {
                'read_only': True
            },
            'updated_at': {
                'read_only': True
            },
        }
    
    # def validate(self, data):
    #     """
    #     Check that either chat_id or user_id is provided, but not both.
    #     """
    #     if 'chat_id' not in data and 'user_id' not in data:
    #         raise serializers.ValidationError("Provide one of chat_id or user_id.")
    #     if 'chat_id' in data and 'user_id' in data:
    #         raise serializers.ValidationError("Provide only one of chat_id or user_id, not both.")
    #     return data

class MessageSendSerializer(serializers.Serializer):
    chat_id = serializers.IntegerField(required=False)
    user_id = serializers.IntegerField(required=False)
    message = serializers.CharField(required=True)

    def validate(self, data):
        if not data.get('chat_id') and not data.get('user_id'):
            raise serializers.ValidationError("Provide chat_id or user_id.")
        if data.get('chat_id') and data.get('user_id'):
            raise serializers.ValidationError("Provide only one of chat_id or user_id.")
        return data
    
class MessageStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageStatus
        fields = ['is_read', 'is_delivered']
        read_only_fields = ['delivered_at', 'read_at']

    def update(self, instance, validated_data):
        # Update timestamps only when status changes to True
        if validated_data.get('is_read', False) and not instance.is_read:
            instance.read_at = timezone.now()
        if validated_data.get('is_delivered', False) and not instance.is_delivered:
            instance.delivered_at = timezone.now()
            
        return super().update(instance, validated_data)