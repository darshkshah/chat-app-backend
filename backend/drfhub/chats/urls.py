from django.urls import path

from . import views

urlpatterns = [
    path('', views.UserChatList.as_view()),
    path('<int:chat_id>/', views.ChatDetailUpdateView.as_view(), name='chat-detail-update'),
    path('user/<int:user_id>/', views.CreateOrFetchChatUsingUserIdView.as_view()),
]