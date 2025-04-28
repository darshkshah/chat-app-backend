from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    pn_country_code = models.CharField(
            max_length=4,
            validators= [ 
                RegexValidator(r'^\+?[0-9]{1,4}$', message="Country code must be 1–4 digits, optionally prefixed with +"),
            ],
            help_text="E.g. '+1', '91'"
        )
    phone_number = models.CharField(
        max_length=10,
        validators=[
            MinLengthValidator(10), 
            MaxLengthValidator(10),
            RegexValidator(r'^[0-9]{10}$', message="Phone number must be exactly 10 digits")
        ],
    )
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to="avatars/%Y/%m/%d/",
        blank=True,
        null=True
    )
    online_status = models.BooleanField(default=False)
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

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()



    def __str__(self):
        return self.username