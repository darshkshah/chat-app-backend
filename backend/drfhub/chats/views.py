from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Prefetch, Count, Q
from chat_messages.models import Message

from rest_framework import views, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Chat, ChatParticipants
from .serializers import ChatSerializer, ChatUpdateSerializer

from users.models import User

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

class CreateOrFetchChatUsingUserIdView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        current_user_id = request.user.user_id
        user = get_object_or_404(User, user_id=user_id)
        print(current_user_id)
        print(user.user_id)

        if (current_user_id == user.user_id):
            return Response({'detail': 'You can\'t create a chat with yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # chat = Chat.objects.filter(participants__user__user_id__in=[current_user_id, user.user_id]).distinct().first()
        chat = Chat.objects.annotate(matched_users=Count('participants', filter=Q(participants__user__user_id__in=[current_user_id, user.user_id]))).filter(matched_users=2).first() # Number of users to match
        if chat:
            return redirect('chat-detail', chat_id=chat.chat_id)
        else:
            chat = Chat.objects.create(
                    is_group=False,
                    is_personal=True
                )
            ChatParticipants.objects.bulk_create([
                    ChatParticipants(chat_id=chat.chat_id, user_id=current_user_id),
                    ChatParticipants(chat_id=chat.chat_id, user_id=user_id)
                ])
            return redirect('chat-detail-update', chat_id=chat.chat_id)

# class ChatDetailView(generics.RetrieveAPIView):
#     serializer_class = ChatSerializer
#     permission_classes = [IsAuthenticated]
#     lookup_field = "chat_id"
#     # queryset = Chat.objects.filter(chat_id=)
#     def get_queryset(self):
#         return Chat.objects.filter(
#             participants__user=self.request.user
#         ).prefetch_related(
#             'participants__user',
#             Prefetch(
#                 'messages',
#                 queryset=Message.objects.order_by('-time_stamp'),
#                 to_attr='latest_messages'
#             )
#         )
    
#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['request_user'] = self.request.user
#         return context

#     def retrieve(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#         except Chat.DoesNotExist:
#             return Response(
#                 {"detail": "Chat not found or access denied"},
#                 status=status.HTTP_403_FORBIDDEN
#             )
        
#         serializer = self.get_serializer(instance)
#         return Response(serializer.data)

class ChatDetailUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = "chat_id"
    http_method_names = ['get', 'patch']  # Allow only GET and PATCH

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

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return ChatUpdateSerializer
        return ChatSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request_user'] = self.request.user
        return context

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