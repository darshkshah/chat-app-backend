from django.urls import path

from . import views

urlpatterns = [
    path('users/', views.users),
    path('users/<int:pk>/', views.user),
    path('add-user/', views.addUser),
    path('update-user/<int:pk>/', views.updateUser),
]