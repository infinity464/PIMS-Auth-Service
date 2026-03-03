from django.urls import path
from .views import RegisterView, LoginView, RoleView, UpdateUserRoleView, UpdateUserEmailView, VerifyTokenView
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path('api/Account/register', RegisterView.as_view()),
    path('api/Account/login', LoginView.as_view()),
    path('api/Account/verifyToken', VerifyTokenView.as_view()),
    path('api/Account/updateUserRole', UpdateUserRoleView.as_view()),
    path('api/Account/updateUserEmail', UpdateUserEmailView.as_view()),
    path("api/roles", RoleView.as_view()),
    path("api/roles/<int:role_id>/", RoleView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
