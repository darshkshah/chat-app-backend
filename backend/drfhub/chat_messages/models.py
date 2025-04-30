from django.db import models, IntegrityError
from users.utils import generate_random_bigint

from users.models import User
from chats.models import Chat

# Create your models here.
class Message(models.Model):
    message_id = models.BigIntegerField(primary_key=True, default=generate_random_bigint, editable=False)
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_id = models.ForeignKey(Chat, on_delete=models.CASCADE)

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
            raise IntegrityError("Could not generate a unique user_id after multiple attempts.")
