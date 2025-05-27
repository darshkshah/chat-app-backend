from django.contrib.auth.models import BaseUserManager

# class UserManager(BaseUserManager):
#     def create_user(self, username, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError("Email is required")
#         if not username:
#             raise ValueError("Username is required")

#         email = self.normalize_email(email)
#         user = self.model(username=username, email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, username, email, password=None, **extra_fields):
#         extra_fields.setdefault("is_staff", True)
#         extra_fields.setdefault("is_superuser", True)
#         return self.create_user(username, email, password, **extra_fields)

class UserManager(BaseUserManager):
    use_in_migrations=True
    def create_user(self, country_code, phone_number, password=None, **extra_fields):
        if not country_code:
            raise ValueError("Country code is required.")
        if not phone_number:
            raise ValueError("Phone number is required.")
        user = self.model(phone_country_code=country_code, phone_number=phone_number, is_phone_verified=True, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, country_code, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(country_code=country_code, phone_number=phone_number, password=password, **extra_fields)