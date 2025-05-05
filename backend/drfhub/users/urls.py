from django.urls import path

from . import views

urlpatterns = [
    path('', views.UserListCreateView.as_view()),
    path('/<int:user_id>/', views.UserRetrieveUpdateView.as_view()),
]