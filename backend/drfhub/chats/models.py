from django.db import models, IntegrityError
from django.db.models import CompositePrimaryKey
from users.utils import generate_random_bigint

from users.models import User


# Create your models here.
class Chat(models.Model):
    chat_id = models.BigIntegerField(primary_key=True, default=generate_random_bigint, editable=False)
    is_group = models.BooleanField()
    is_personal = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Custom save function for User model
    def save(self, *args, **kwargs):
        if not self.chat_id:
            self.chat_id = generate_random_bigint()

        max_retries = 5
        for _ in range(max_retries):
            try:
                # print(f"Iteration: {_}")
                super().save(*args, **kwargs)
                break
            except IntegrityError:
                # Likely a duplicate user_id
                self.chat_id = generate_random_bigint()
        else:
            raise IntegrityError("Could not generate a unique chat_id after multiple attempts.")

    def __str__(self):
        chat_type = "Group" if self.is_group else "Private"
        formatted_date = self.created_at.strftime("%d/%m/%Y %H:%M:%S")
        return f"{chat_type} Chat #{self.chat_id} (created on {formatted_date})"

class ChatParticipants(models.Model):
    pk = CompositePrimaryKey("chat", "user")
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat Participant #{self.user.user_id} of Chat #{self.chat.chat_id}"

