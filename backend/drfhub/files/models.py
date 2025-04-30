from django.db import models
from users.utils import generate_random_bigint
from users.models import User


# Create your models here.
class File(models.Model):
    file_id = models.BigIntegerField(primary_key=True, default=generate_random_bigint, editable=False)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='files'
    )
    