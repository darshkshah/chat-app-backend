from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Prefetch

from chats.models import Chat
from chat_messages.models import Message, MessageStatus

from pprint import pprint

class Command(BaseCommand):
    help = "View Chat Participants"

    def handle(self, *args, **options):

        # chat = Chat.objects.filter(is_personal=True).filter(participants__user_id=146706994687613862).filter(participants__user_id=908666851195169147).first()

        # # chat = Chat.objects.filter(
        # #     is_personal=True,
        # #     participants__user_id__in=[146706994687613862, 5155144139330333]
        # # ).first()
        # print(chat)
        # # pprint(connection.queries)

        # participants = chat.participants.all()
        # for cp in participants:
        #     print(f"{cp.user.username} {cp.user.user_id} {cp.user.bio} {cp.joined_at.strftime("%d/%m/%Y %H:%M:%S")}")
        # pprint(connection.queries)
        # print(f"Total queries run: {len(connection.queries)}")
        # return super().handle(*args, **options)

        # chat = Chat.objects.filter(participants__user__username = 'darshshah2109')
        # print(chat)

        # messageStatuses = MessageStatus.objects.select_related('message').all()
        # for messageStatus in messageStatuses:
        #     print(f"{messageStatus.message.message} - {messageStatus.message.time_stamp}")

        # chats = Chat.objects.prefetch_related('participants__user').all()
        # for index, chat in enumerate(chats):
        #     print(f"Chat {index+1} (id: {chat.chat_id})")
        #     for participant in chat.participants.all():
        #         print(f"{participant.user.first_name} {participant.user.last_name} {participant.user.username}")

        # Not Working
        # chats = Chat.objects.all()
        # for index, chat in enumerate(chats):
        #     print(f"Chat {index+1} (id: {chat.chat_id})")
        #     for message in chat.messages.all():
        #         print(f"{message.message} {message.messagestatus}")
        # chats = Chat.objects.prefetch_related('messages__messagestatus').all()
        # chats = Chat.objects.prefetch_related(
        #         Prefetch(
        #             'messages__messagestatus',
        #             queryset=MessageStatus.objects.select_related('user')
        #         )
        #     ).all()
        # chats = Chat.objects.all()
        chats = Chat.objects.prefetch_related('messages').all()
        for index, chat in enumerate(chats):
            print(f"Chat {index+1} (id: {chat.chat_id})")
            for message in chat.messages.all():
                print(f"  Message: {message.message} {message.time_stamp}")
                for status in message.messagestatus.all():
                    print(f"    User: {status.user.first_name} {status.user.last_name} | Read: {status.is_read} at {status.read_at}")
        pprint(connection.queries)
        print(len(connection.queries))