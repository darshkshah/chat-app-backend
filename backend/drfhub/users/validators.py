from django.core.validators import RegexValidator

country_code_validator = RegexValidator(r'^\+[0-9]{1,4}$', message="Country code must be 1–4 digits, prefixed with +")
phone_number_validator = RegexValidator(r'^[0-9]{10}$', message="Phone number must be exactly 10 digits")
otp_validator = RegexValidator(r'^\d{6}$', 'An OTP must be 6 digits.')