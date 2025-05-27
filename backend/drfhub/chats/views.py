from django.shortcuts import render
from django.db.models import Prefetch
from chat_messages.models import Message

from rest_framework import views, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Chat, ChatParticipants
from .serializers import ChatSerializer

# Create your views here.

class UserChatList(generics.ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(
            participants__user=self.request.user
        ).prefetch_related(
            'participants__user',
            Prefetch(
                'messages',
                queryset=Message.objects.order_by('-time_stamp'),
                to_attr='latest_messages'
            )
        ).order_by('-updated_at')

    def get_serializer_context(self):
        return {'request_user': self.request.user}

class ChatDetailView(generics.RetrieveAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "chat_id"
    # queryset = Chat.objects.filter(chat_id=)
    def get_queryset(self):
        return Chat.objects.filter(
            participants__user=self.request.user
        ).prefetch_related(
            'participants__user',
            Prefetch(
                'messages',
                queryset=Message.objects.order_by('-time_stamp'),
                to_attr='latest_messages'
            )
        )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Chat.DoesNotExist:
            return Response(
                {"detail": "Chat not found or access denied"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # def get_queryset(self):
    #     chat = Chat.objects.filter(chat_id = self.request.)
    #     return super().get_queryset()
    