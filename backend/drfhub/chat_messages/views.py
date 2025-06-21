from django.shortcuts import get_object_or_404
# from django.db.models import Count, Q
from django.utils import timezone

from rest_framework import status, views, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from chats.models import Chat, ChatParticipants
from .models import Message, MessageStatus
from users.models import User
from .serializers import MessageSerializer, DateTimeRequestSerializer, MessageSendSerializer, MessageStatusSerializer
# Create your views here.

class MessageSendAPIView(views.APIView):
    """
    API view to handle sending and retrieving messages.
    
    GET: Retrieve messages for a chat, optionally filtered by timestamp
    POST: Send a new message to a chat or user
    """
    http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get messages from a chat, with optional timestamp filtering.
        
        Query Parameters:
        - chat_id: ID of the chat to retrieve messages from
        - timestamp (optional): Only return messages newer than this timestamp
        """
        serializer = DateTimeRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                {
                    "detail": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.user.user_id
        data = serializer.validated_data
        chat_id = data['chat_id']
        if not ChatParticipants.objects.filter(chat_id=chat_id, user_id=user_id).exists():
            return Response(
                {
                    "detail": "You are not authorized to view messages in this chat"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        timestamp = data.get('timestamp')

        messages_query = Message.objects.filter(chat_id=chat_id)
        if 'timestamp' in data:
            messages_query = messages_query.filter(time_stamp__gt=timestamp)
        messages = messages_query.order_by('time_stamp')
        response_serializer = MessageSerializer(messages, many=True)
        return Response(
            {
                "messages": response_serializer.data
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        """
        Send a new message.
        
        Request Body:
        - chat_id OR user_id: Target chat or user to send message to
        - message: Content of the message to send
        """
        # sender = request.user
        sender_id = request.user.user_id
        serializer = MessageSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        chat_id = data.get('chat_id')
        recipient_id = data.get('user_id')
        user_message = data.get("message")
        
        chat = None
        if chat_id:
            chat = get_object_or_404(Chat, pk=chat_id)
            if not ChatParticipants.objects.filter(chat_id=chat_id, user_id=sender_id).exists():
                return Response(
                    {
                        "detail": "You are not authorized to send messages in this chat"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            if int(recipient_id) == sender_id:
                return Response(
                    {
                        "detail": "You can not message yourself."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            get_object_or_404(User, pk=recipient_id)
            chat = Chat.objects.filter(is_personal=True).filter(participants__user_id=sender_id).filter(participants__user_id=recipient_id).first()
            # chat = Chat.objects.annotate(num_participants=Count('participants')).filter(
            #         Q(participants__user_id=sender_id) & 
            #         Q(participants__user_id=recipient_id),
            #         num_participants=2,
            #         is_personal=True
            #     ).first()
            if not chat:
                chat = Chat.objects.create(
                    is_group=False,
                    is_personal=True
                )
                ChatParticipants.objects.bulk_create([
                    ChatParticipants(chat_id=chat.chat_id, user_id=sender_id),
                    ChatParticipants(chat_id=chat.chat_id, user_id=recipient_id)
                ])
        
        message = Message.objects.create(
            sender_id=sender_id,
            chat_id=chat.chat_id,
            message=user_message,
            is_file=False
        )
        
        chat.updated_at = timezone.now()
        chat.save(update_fields=['updated_at'])
        
        status_objects = []
        for participant in ChatParticipants.objects.filter(chat=chat).exclude(user_id=sender_id):
            status_objects.append(
                MessageStatus(
                    message_id=message.message_id,
                    user_id=participant.user_id,
                    is_delivered=False,
                    is_read=False
                )
            )
        
        if status_objects:
            MessageStatus.objects.bulk_create(status_objects)
            
        serializer = MessageSerializer(message)

        return Response(
            {
                "message": serializer.data,
            }, 
            status=status.HTTP_201_CREATED
        )
    
class MessageStatusUpdateView(generics.UpdateAPIView):
    serializer_class = MessageStatusSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']
    # lookup_field = 'message_id'

    def get_object(self):
        message_id = self.kwargs['message_id']
        user = self.request.user
        # Get message and check chat membership
        message = get_object_or_404(Message, message_id=message_id)
        if not ChatParticipants.objects.filter(chat=message.chat, user=user).exists():
            raise PermissionDenied("You're not part of this chat")
        # Check if user is the message sender (shouldn't have status entry)
        if message.sender == user:
            raise PermissionDenied("Senders cannot update message status")
        # Get status object or 404
        status_obj = get_object_or_404(MessageStatus, message=message, user=user)
        return status_obj

    def patch(self, request, *args, **kwargs):
        try:
            return super().patch(request, *args, **kwargs)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)