from django.urls import path

from . import views

urlpatterns = [
    # path('<int:user_id>/', views.MessageCreateAPIView.as_view()),
    path('send/', views.MessageSendAPIView.as_view()),
    path('<int:message_id>/status', views.MessageStatusUpdateView.as_view())
]