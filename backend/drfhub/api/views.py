from django.shortcuts import get_object_or_404
from django.forms.models import  model_to_dict
from django.contrib.auth import authenticate
from django.utils import timezone

from rest_framework import status, views
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission

from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from .serializers import UserSerializer, LoginSerializer

# Create your views here.

class LoginView(views.APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user=authenticate(**serializer.validated_data)
        if not user:
            return Response({
                    "error": "Invalid Credentials"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        refresh = RefreshToken.for_user(user=user)

        return Response({
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        })


class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserDetailAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_url_kwarg = 'user_id'
    permission_classes = [IsAuthenticated]


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Custom response if needed
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

# class UserCreateView(generics.CreateAPIView):
#     serializer_class = UserSerializer

#     def create(self, request, *args, **kwargs):
#         data = request.data.copy()
#         password = data.pop('password', None)

#         if not password:
#             return Response({"response": "Password can not be empty"})
        
#         serializer = self.get_serializer(data=data)

#         if serializer.is_valid():
#             user = serializer.save()

#             if password:
#                 user.set_password(password)
#                 user.save()
            
#             return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserUpdateView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'user_id'
    
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
    

# class UserUpdatePermission(BasePermission):
#     """
#     Custom permission to only allow users to edit their own profile.
#     """
#     def has_permission(self, request, view):
#         # Check if user is authenticated
#         return request.user and request.user.is_authenticated
        
#     def has_object_permission(self, request, view, obj):
#         # Check if the user is trying to edit their own profile
#         return obj.user_id == request.user.user_id

# class UserUpdateView(generics.UpdateAPIView):
#     serializer_class = UserSerializer
#     queryset = User.objects.all()
#     permission_classes = [IsAuthenticated, UserUpdatePermission]
#     lookup_url_kwarg = 'user_id'
    
#     def update(self, request, *args, **kwargs):
#         user = self.get_object()

#         if user.user_id != request.user.user_id:
#             return Response(
#                 {"error": "You do not have permission to update this user's profile"},
#                 status=status.HTTP_403_FORBIDDEN
#             )

#         password = request.data.get("password")
#         if password:
#             data = request.data.copy()
#             data.pop('password')

#             user.set_password(password)
#             user.save()
#         else:
#             data = request.data
        
#         serializer = self.get_serializer(user, data=data, partial=True)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# @api_view(["GET"])
# def users(request, *args, **kwargs):

#     # if request.method == "GET":
#     #     return Response({"detail": '"GET" not allowed no no no'}, status=404)

#     users = User.objects.all()
#     serializer = UserSerializer(users, many=True)
#     return Response(serializer.data)

# @api_view(["PATCH"])
# def updateUser(request, pk):
#     user = get_object_or_404(User, pk=pk)
    
#     password = request.data.get("password")
#     if password:
#         data = request.data.copy()
#         data.pop('password')

#         user.set_password(password)
#         user.save()
#     else:
#         data = request.data

#     serializer = UserSerializer(user, data=data, partial=True)

#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(["POST"])
# def addUser(request):
#     data = request.data.copy()
#     password = data.pop('password', None)

#     if not password:
#         return Response({"response": "Password can not be empty"})

#     serializer = UserSerializer(data=data)

#     if serializer.is_valid():
#         user = serializer.save()
#             # Now set the password properly if it was provided

#         if password:
#             user.set_password(password)
#             user.save()

#         return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(["GET"])
# def user(request, pk):
#     user = get_object_or_404(User, pk=pk)
#     serializer = UserSerializer(user)
#     return Response(serializer.data)

# class UserUpdateView(generics.UpdateAPIView):
#     serializer_class = UserSerializer
#     queryset = User.objects.all()
#     lookup_url_kwarg = 'user_id'
    
#     def update(self, request, *args, **kwargs):
#         user = self.get_object()
#         password = request.data.get("password")

#         if password:
#             data = request.data.copy()
#             data.pop('password')

#             user.set_password(password)
#             user.save()
#         else:
#             data = request.data
        
#         serializer = self.get_serializer(user, data=data, partial=True)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class LoginView(views.APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         username = request.data.get("username", "")
#         password = request.data.get("password", "")

#         if not username or not password:
#             return Response(
#                 {"error": "Please provide both username and password"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         user = authenticate(username=username, password=password)

#         if user:
#             refresh = RefreshToken.for_user(user)
            
#             return Response({
#                 "user": {
#                     "user_id": user.user_id,
#                     "username": user.username,
#                     "email": user.email,
#                     "first_name": user.first_name,
#                     "last_name": user.last_name,
#                     "phone_number": user.phone_number,
#                     "is_staff": user.is_staff,
#                     # Add any other user fields you want to return
#                 },
#                 "refresh": str(refresh),
#                 "access": str(refresh.access_token),
#             }, status=status.HTTP_200_OK)
#         else:
#             return Response(
#                 {"error": "Invalid credentials"},
#                 status=status.HTTP_401_UNAUTHORIZED
#             )

























    # data = {}
    # if model_data:
    #     data = model_to_dict(model_data, fields=['id', 'last_login', 'is_superuser', 'first_name', 'last_name', 'username', 'pn_country_code', 'phone_number', 'email', 'bio', 'online_status', 'created_at', 'is_active', 'is_staff'])

    # return Response(data)


# ['id', 'password', 'last_login', 'is_superuser', 'first_name', 'last_name', 'username', 'pn_country_code', 'phone_number', 'email', 'bio', 'avatar', 'online_status', 'created_at', 'is_active', 'is_staff']

































































# def api_home(request, *args, **kwargs):
#     model_data = User.objects.all().order_by('?').first()
#     data = {}
#     if model_data:
#         data = model_to_dict(model_data, fields=['id', 'last_login', 'is_superuser', 'first_name', 'last_name', 'username', 'pn_country_code', 'phone_number', 'email', 'bio', 'online_status', 'created_at', 'is_active', 'is_staff'])

#     return JsonResponse(data)

# def api_home(request, *args, **kwargs):
#     model_data = User.objects.all().order_by('?').first()
#     data = {}
#     if model_data:
        # data["id"] = model_data.id
        # data["first_name"] = model_data.first_name
        # data["last_name"] = model_data.last_name
        # data["phone_number"] = f"{model_data.pn_country_code} {model_data.phone_number}"
        # data["email"] = model_data.email
        # data["bio"] = model_data.bio
        # data["online_status"] = model_data.online_status
        # data["last_login"] = model_data.last_login
        # data["created_at"] = model_data.created_at

    # return JsonResponse(data)


# def api_home(request, *args, **kwargs):
#     print("REQUEST: ")
#     # print(request.scheme)
#     print(request.body)
#     print(request.path)
#     print(request.method)
#     print(request.GET['abc'])
#     print(request.POST)
#     dictionary = dict(request.GET)
#     print(len(list(dictionary.keys())))
#     # print(request.headers)
#     return JsonResponse({"message": "Hi there, this is a Django API Response!!"})
