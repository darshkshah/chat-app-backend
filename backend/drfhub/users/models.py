from django.db import models, IntegrityError
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now

import random
from datetime import timedelta

from .utils import generate_random_bigint
from .managers import UserManager
from .validators import phone_number_validator, country_code_validator

# Create your models here.
def user_avatar_path(instance, filename):
    return f"avatars/{instance.user_id}/{filename}"

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.BigIntegerField(primary_key=True, default=generate_random_bigint, editable=False)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    username = models.CharField(max_length=100, unique=True, blank=True, null=True)
    phone_country_code = models.CharField(
            max_length=4,
            validators= [country_code_validator],
            help_text="E.g. '+1', '91'",
            null=False,
            blank=False
        )
    phone_number = models.CharField(
        max_length=10,
        validators=[MinLengthValidator(10), MaxLengthValidator(10), phone_number_validator],
        unique=True,
        null=False,
        blank=False
    )
    is_phone_verified = models.BooleanField(default=False, null=False, blank=False)
    email = models.EmailField(unique=True, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        blank=True,
        null=True
    )
    online_status = models.BooleanField(default=False, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. "
            "Group permissions are aggregated."
        ),
        related_name="users_custom_group_set",
        related_query_name="user"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="users_custom_permission_set",
        related_query_name="user"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

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

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name} ({self.phone_number})"
        elif self.username:
            return f"{self.username} ({self.phone_number})"
        return self.phone_number

class OTP(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    phone_country_code = models.CharField(max_length=4, null=False, blank=False, validators=[country_code_validator])
    phone_number = models.CharField(max_length=10, null=False, blank=False, validators=[phone_number_validator])
    otp = models.CharField(max_length=6, null=False, blank=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        unique_together = ('phone_country_code', 'phone_number')
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    @classmethod
    def generate_otp(cls, phone_country_code, phone_number):
        otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        created_at = now()
        expires_at = created_at + timedelta(minutes=10)
        otp_obj, created = cls.objects.update_or_create(
            phone_country_code = phone_country_code,
            phone_number=phone_number,
            defaults={'otp': otp_code, 'is_verified': False, 'expires_at': expires_at, 'created_at': created_at}
        )
        return otp_code