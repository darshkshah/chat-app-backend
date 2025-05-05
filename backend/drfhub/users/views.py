from django.contrib.auth import authenticate
from django.utils import timezone


from rest_framework import status, views, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, UserSerializer
from .models import User


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
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })

class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
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
