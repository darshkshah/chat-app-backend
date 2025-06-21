from django.contrib.auth import authenticate
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models.functions import Concat

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


from rest_framework import status, views, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from rest_framework_simplejwt.tokens import RefreshToken

from drfhub.settings import ACCOUNT_SSID, AUTH_TOKEN

from .serializers import LoginSerializer, SendOtpSerializer, UserSerializer, VerifyOTPSerializer
from .models import OTP, User

client = Client(ACCOUNT_SSID, AUTH_TOKEN)
# Create your views here.

# class LoginView(views.APIView):
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         user=authenticate(**serializer.validated_data)
#         if not user:
#             return Response({
#                     "error": "Invalid Credentials"
#                 },
#                 status=status.HTTP_401_UNAUTHORIZED
#             )
        
#         user.last_login = timezone.now()
#         user.save(update_fields=['last_login'])

#         refresh = RefreshToken.for_user(user=user)

#         return Response({
#             "refresh": str(refresh),
#             "access": str(refresh.access_token),
#             "user_id": user.user_id
#         })

class RequestOTPView(views.APIView):
    def post(self, request):
        serializer = SendOtpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        country_code=serializer.validated_data['country_code']
        phone_number=serializer.validated_data['phone_number']
        otp = OTP.generate_otp(phone_country_code=country_code, phone_number=phone_number)
        # print(country_code)
        # print(phone_number)
        # Twilio send OTP code here UNCOMMENT later
        # try:
        #     message=client.messages.create(
        #         body=f"Your OTP is {otp}. Do not share it with anyone under any circumstance.",
        #         from_="+12792393326",
        #         to=f"{country_code}{phone_number}"
        #     )
        # except TwilioRestException as e:
        #     return Response({
        #             'detail': f'Could not send message to {country_code}{phone_number}. As the phone number is not verified with twilio. To send messages to unverified numbers upgrade to a premium subscription on twilio', 
        #         },
        #         status=status.HTTP_403_FORBIDDEN
        #     )
        # print(message.body)
        return Response({'message': f'OTP {otp} sent successfully to {country_code}{phone_number}'}, status=status.HTTP_200_OK)

class VerifyOTPView(views.APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        country_code=serializer.validated_data['country_code']
        phone_number=serializer.validated_data['phone_number']
        otp=serializer.validated_data['otp']

        otp_obj = OTP.objects.get(phone_number=phone_number, phone_country_code=country_code)
        otp_obj.is_verified = True
        otp_obj.save()
        
        boolean_ = User.objects.filter(phone_country_code=country_code, phone_number=phone_number).exists()
        if not boolean_:
            user = User.objects.create_user(country_code=country_code, phone_number=phone_number)
            status_code = status.HTTP_201_CREATED
        else:
            user = User.objects.get(phone_country_code=country_code, phone_number=phone_number)
            status_code = status.HTTP_200_OK

        serializer = UserSerializer(user)

        refresh = RefreshToken.for_user(user=user)

        return Response({'data': serializer.data, 'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status_code)

class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.request.query_params.get("user_id")
        phone_number = self.request.query_params.get("phone_number")
        
        if self.request.method == 'GET':
            if user_id and phone_number:
                raise ValidationError("Provide only one of 'user_id' and 'phone_number'.")
            if user_id:
                return get_object_or_404(User, user_id=user_id)
            if phone_number:
                # print(phone_number)
                # phone_number = f"+{phone_number.replace(' ', '')}"
                # print(phone_number)
                user = next(
                    (u for u in User.objects.only('user_id', 'phone_country_code', 'phone_number')
                    if f"{u.phone_country_code}{u.phone_number}" == phone_number),
                    None
                )
                if not user:
                    raise Http404("User not found with that phone number")
                return user
            raise ValidationError("You must provide either 'user_id' or both 'phone_country_code' and 'phone_number'.")
        if not user_id:
            raise ValidationError("You must provide 'user_id' for updates.")
        return get_object_or_404(User, user_id=user_id)
        
    def update(self, request, *args, **kwargs):
        user = self.get_object()

        if user.user_id != request.user.user_id:
            return Response(
                {"error": "You do not have permission to update this user's profile"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

# REMOVE THE CREATE API VIEW FROM HERE LATER SINCE WE WILL DO THIS IN VERIFY OTP VIEW
class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Custom response if needed
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
    
    def get_permissions(self):
        if self.request.method == 'POST':  # Create operation
            return []  # No permissions required for user creation
        return [IsAuthenticated()]
    
    def list(self, request, *args, **kwargs):
        only_phone = request.query_params.get('only_phone_number') == 'true'
        if only_phone:
            data = list(User.objects.annotate(full_phone=Concat('phone_country_code', 'phone_number')).values_list('full_phone', flat=True))
            return Response(data, status=status.HTTP_200_OK)
        return super().list(request, *args, **kwargs)