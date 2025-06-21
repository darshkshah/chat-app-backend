from django.urls import path

from . import views

urlpatterns = [
    path('sendotp/', views.RequestOTPView.as_view()),
    path('verifyotp/', views.VerifyOTPView.as_view()),
    path('', views.UserListCreateView.as_view()),
    path('specific/', views.UserRetrieveUpdateView.as_view()),
]