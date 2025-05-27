from django.urls import path

from . import views

urlpatterns = [
    path('', views.UserChatList.as_view()),
    path('<int:chat_id>/', views.ChatDetailView.as_view()),
]