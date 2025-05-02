from django.db import models, IntegrityError
from users.utils import generate_random_bigint

from users.models import User
from chats.models import Chat
from files.models import File

# Create your models here.
class Message(models.Model):
    message_id = models.BigIntegerField(primary_key=True, default=generate_random_bigint, editable=False)
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_id = models.ForeignKey(Chat, on_delete=models.CASCADE)
    file_id = models.ForeignKey(File, on_delete = models.CASCADE)
    time_stamp = models.DateTimeField(auto_created=True)
    message = models.TextField(blank=True)
    is_file = models.BooleanField()
    updated_at = models.DateTimeField(auto_now_add=True)

    # Custom save function for User model
    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = generate_random_bigint()

        max_retries = 5
        for _ in range(max_retries):
            try:
                # print(f"Iteration: {_}")
                super().save(*args, **kwargs)
                break
            except IntegrityError:
                # Likely a duplicate user_id
                self.user_id = generate_random_bigint()
        else:
            raise IntegrityError("Could not generate a unique message_id after multiple attempts.")
        
class MessageStatus(models.Model):
    unique_id = models.BigIntegerField(primary_key=True, default=generate_random_bigint, editable=False)
    message_id = models.ForeignKey(Message, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    is_delivered = models.BooleanField()
    is_read = models.BooleanField()
    delivered_at = models.DateTimeField()
    read_at = models.DateTimeField()

    # Custom save function for User model
    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = generate_random_bigint()

        max_retries = 5
        for _ in range(max_retries):
            try:
                # print(f"Iteration: {_}")
                super().save(*args, **kwargs)
                break
            except IntegrityError:
                # Likely a duplicate user_id
                self.user_id = generate_random_bigint()
        else:
            raise IntegrityError("Could not generate a unique unique_id after multiple attempts.")
