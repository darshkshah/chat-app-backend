import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from django.db.models import Subquery

from chats.models import ChatParticipants, Chat
from users.serializers import UserSerializer

from .models import Message
from .serializers import MessageSerializer

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            self.close()
        else:
            print(f"\033[94m{self.user} Connected...\033[0m")
            self.chat_ids = get_user_chat_ids(self.user)
            for chat_id in self.chat_ids:
                print(f"Connecting {self.user} to chat {chat_id}")
                async_to_sync(self.channel_layer.group_add) (
                    f"chat_{chat_id}",
                    self.channel_name
                )
            self.user_ids = get_relevant_user_profile_update_streams(self.user)
            for user_id in self.user_ids:
                print(f"Connecting {self.user} to user profile updates of {user_id}")
                async_to_sync(self.channel_layer.group_add) (
                    f"user_{user_id}",
                    self.channel_name
                )
            self.accept()

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        print(data)
        if "type" not in data:
            self.send(text_data=json.dumps({
                "type": "badRequest",
                "data": "There must be a 'type' in request"
            }))
            self.close()
            return
        if data['type'] == 'ping':
            return
        elif data['type'] == 'newMessage':
            chat_id = data["chat_id"]
            message_text = data["message"]
            is_file = data.get("is_file", False)
            file_id = data.get("file_id")
            sender = self.user

            message = Message.objects.create(
                sender=sender,
                chat_id=chat_id,
                message=message_text,
                is_file=is_file,
                file_id=file_id
            )

            serialized = MessageSerializer(message).data
            
            async_to_sync(self.channel_layer.group_send) (
                f"chat_{chat_id}",
                {
                    "type": "chat_message",
                    "message": serialized
                }
            )
        elif data['type'] == 'userProfileUpdate':
            if 'user_id' not in data:
                self.send(text_data=json.dumps({
                    'type': 'badRequest',
                    'data': 'user_id must be there in the request'
                }))
                self.close()
                return
            if data['user_id'] != str(self.user.user_id):
                self.send(text_data=json.dumps({
                    'type': 'badRequest',
                    'data': 'you can not update the profile of another user'
                }))
                self.close()
                return
            serializer = UserSerializer(instance=self.user, data=data, partial=True)
            # Check if any updatable fields are present in the input
            updatable_fields = set(serializer.fields.keys()) - {
                field for field, config in serializer.fields.items()
                if config.read_only or config.write_only
            }
            incoming_fields = set(data.keys())

            if not incoming_fields & updatable_fields:
                self.send(text_data=json.dumps({
                    'type': 'nothingToUpdate',
                    'data': {
                        'message': 'No updatable fields were provided.',
                        'updatable_fields': list(updatable_fields)
                    }
                }))
                return
            if serializer.is_valid():
                user = serializer.save()
                updated_fields = {field: getattr(user, field) for field in serializer.validated_data.keys()}
                self.send(text_data=json.dumps({
                    'type': 'userProfileUpdate', # userProfileUpdate
                    'user_id': str(self.user.user_id),
                    'data': updated_fields
                }))
                async_to_sync(self.channel_layer.group_send) (
                    f"user_{self.user.user_id}",
                    {
                        "type": "user_profile_update",
                        "user_id": str(self.user.user_id),
                        "message": updated_fields
                    }
                )
            else:
                self.send(text_data=json.dumps({
                    'type': 'badRequest',
                    'data': serializer.errors
                }))

        else:
            self.send(text_data=json.dumps({
                "type": "badRequest",
                "data": f"No type with {data['type']} exists"
            }))
            self.close()
            return

    
    def disconnect(self, close_code):
        print(f"Disconnect: {hasattr(self, 'chat_ids')}")
        if hasattr(self, 'chat_ids'):
            for chat_id in self.chat_ids:
                print(f"Disconnecting {self.user} from {chat_id}")
                self.channel_layer.group_discard(f"chat_{chat_id}", self.channel_name)
        if hasattr(self, 'user_ids'):
            for user_id in self.user_ids:
                print(f"Disconnecting {self.user} from {user_id}")
                self.channel_layer.group_discard(f"user_{user_id}", self.channel_name)
        print(f"Disconnected {self.user}...")
    
    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'type': 'newMessage',
            'data': message
        }))
    
    def user_profile_update(self, event):
        message = event['message']
        user_id = event['user_id']
        self.send(text_data=json.dumps({
            'type': 'userProfileUpdate',
            'user_id': user_id,
            'data': message
        }))

def get_user_chat_ids(user):
    return [participant.chat.chat_id for participant in ChatParticipants.objects.filter(user = user)]

def get_relevant_user_profile_update_streams(user):
    user_id = user.user_id
    chats = ChatParticipants.objects.filter(user=user_id).values_list('chat', flat=True)
    relevant_user_ids = ChatParticipants.objects.filter(
        chat__in=Subquery(chats)
    ).exclude(user=user_id).values_list('user', flat=True)
    return relevant_user_ids

# def get_relevant_user_profile_update_streams(user):
#     user_id = user.user_id
#     chats = ChatParticipants.objects.filter(user=user_id).values_list('chat', flat=True)
#     relevant_user_ids = ChatParticipants.objects.filter(chat__in=chats).exclude(user=user_id).values_list('user', flat=True)
#     return relevant_user_ids