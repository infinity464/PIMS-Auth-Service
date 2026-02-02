# urls.py
from django.urls import path
from .views import UserListView

urlpatterns = [
    path('api/users/', UserListView.as_view(), name='user-list'),
]
