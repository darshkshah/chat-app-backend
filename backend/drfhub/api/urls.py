from django.urls import path

from . import views

urlpatterns = [
    path('users/', views.UserListAPIView.as_view()),
    path('users/<int:user_id>/', views.UserDetailAPIView.as_view()),
    path('add-user/', views.UserCreateView.as_view()),
    path('update-user/<int:pk>/', views.UserUpdateView.as_view()),
]