from django.db import models, IntegrityError
from users.utils import generate_random_bigint

from users.models import User
from chats.models import Chat
from files.models import File

# Create your models here.
class Message(models.Model):
    message_id = models.BigIntegerField(primary_key=True, default=generate_random_bigint, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    file = models.ForeignKey(File, on_delete = models.CASCADE, blank=True, null=True)
    time_stamp = models.DateTimeField(auto_created=True, auto_now_add=True)
    message = models.TextField(blank=True)
    is_file = models.BooleanField()
    updated_at = models.DateTimeField(auto_now_add=True)

    # Custom save function for User model
    def save(self, *args, **kwargs):
        if not self.message_id:
            self.message_id = generate_random_bigint()

        max_retries = 5
        for attempt in range(max_retries):
            try:
                return super().save(*args, **kwargs)
            except IntegrityError as e:
                if 'message_id' in str(e):
                    self.message_id = generate_random_bigint()
                else:
                    raise  # Re-raise other integrity errors

        raise IntegrityError("Could not generate a unique message_id after multiple attempts.")

class MessageStatus(models.Model):
    unique_id = models.BigIntegerField(primary_key=True, default=generate_random_bigint, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='messagestatus')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_delivered = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True)
    read_at = models.DateTimeField(null=True)

    # Custom save function for User model
    def save(self, *args, **kwargs):
        if not self.unique_id:
            self.unique_id = generate_random_bigint()
        # return super().save(*args, **kwargs)
        max_retries = 5
        for _ in range(max_retries):
            try:
                # print(f"Iteration: {_}")
                return super().save(*args, **kwargs)
            except IntegrityError:
                # Likely a duplicate message_id
                self.unique_id = generate_random_bigint()
        
        raise IntegrityError("Could not generate a unique unique_id after multiple attempts.")
